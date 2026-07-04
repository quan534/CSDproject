from models import User
from typing import Optional

class AVLNode:
    """Node nội bộ của AVL Tree.  value = User object."""
    def __init__(self, user: User):       #
        self.user   = user
        self.left   = None
        self.right  = None
        self.height = 1            # dùng để tính balance factor


class AVLTree:
    """
    Cây AVL tự cân bằng — thay thế BST thuần để đảm bảo O(log n) mọi lúc.

    Hỗ trợ tìm kiếm chính xác theo tên VÀ range-search theo tuổi
    (nếu build AVL thứ hai theo age làm key).

    Tất cả thuật toán tự implement, không dùng thư viện ngoài.
    """

    def __init__(self):
        self.root = None

    # ── INTERNAL HELPERS ──────────────────────────────────────────────
    def height(self, node: AVLNode) -> int:
        if node is None:
            return 0
        left = self._height(node.left)
        right = self._height(node.right)
        return 1 + max(left,right)
        """Trả về height của node (0 nếu None)."""
        pass

    def balance_factor(self, node: AVLNode) -> int:
        blf = self._height(node.left) - self.height(node.right)
        return blf
        """
        Tính balance factor = height(left) - height(right).
        AVL yêu cầu giá trị này luôn trong [-1, 0, 1].
        """
        pass
    
    def update_height(self, node: AVLNode) -> None:
        if node is None:
            return
        left = node.left.height if node.left is not None else -1
        right = node.right.height if node.right is not None else -1
        node.height =1 + max(left,right)
        return
        """Cập nhật lại height sau khi rotate."""
        pass

    def rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self.update_height(y)
        self.update_height(x)
        return x
    
    def rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self.update_height(x)
        self.update_height(y)
        return y

    def rebalance(self, node: AVLNode) -> AVLNode:
        """Kiểm tra balance factor và gọi rotate phù hợp (LL, RR, LR, RL)."""
        if node is None:
            return node

        # 1. Cập nhật lại chiều cao của nút hiện tại
        self.update_height(node)

        # 2. Lấy chỉ số cân bằng
        balance = self._balance_factor(node)

        # Trường hợp Trái Trái (LL)
        if balance > 1 and self.balance_factor(node.left) >= 0:
            return self.rotate_right(node)

        # Trường hợp Trái Phải (LR)
        if balance > 1 and self.balance_factor(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Trường hợp Phải Phải (RR)
        if balance < -1 and self.balance_factor(node.right) <= 0:
            return self.rotate_left(node)

        # Trường hợp Phải Trái (RL)
        if balance < -1 and self.balance_factor(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node  # Không mất cân bằng, trả về nút cũ

    def insert_recursive(self, node,user) -> AVLNode:
        """Đệ quy insert + rebalance trên đường về."""
        
        if node is None:
            return AVLNode(user)
        if user.id > node,user.id:
            node.right = self.insert_recursive(node.right,user)
        elif user.id < node.user.id:
            node.left = self.insert_recursive(node.left,user)
        else:
            return node
        return self.rebalance(node)

    def delete_recursive(self, node: Optional[AVLNode], user_id: int):
        """Đệ quy xóa nút và tái cân bằng hệ thống."""
        if node is None:
            return node

        if user_id < node.user.id:
            node.left = self.delete_recursive(node.left, user_id)
        elif user_id > node.user.id:
            node.right = self.delete_recursive(node.right, user_id)
        else:
            # Nút cần xóa nằm ở đây
            if node.left is None or node.right is None:
                temp = node.left if node.left else node.right
                if temp is None:
                    node = None
                else:
                    node = temp  # Sao chép các liên kết con
            else:
                # Nút có 2 con: tìm nút thay thế nhỏ nhất bên phải
                temp = self.min_node(node.right)
                node.user = temp.user
                node.right = self.delete_recursive(node.right, temp.user.id)

        if node is None:
            return node
        return self.rebalance(node)
    
    def min_node(self, node: AVLNode) -> AVLNode:
        if node == None:
            return
        current = node
        while current.left is not None:
            current = current.left
        return current
        """Tìm node nhỏ nhất (ngoài cùng bên trái)."""
        pass

    # ── PUBLIC API ────────────────────────────────────────────────────

    def insert(self, user: User) -> None:
        """
        Thêm user vào AVL Tree theo key = name.

        Args:
            user (User): User cần thêm

        Returns:
            None
        """
        self.insert_recursive(self.root,user)
        return

    def delete(self, id: str) -> None:
        """
        Xóa node có key = name khỏi cây.

        Args:
            name (str): tên của user cần xóa

        Returns:
            None
        """
        self.delete_recursive(self.root, id)

    def search_exact(self, name: str) -> Optional[User]:
        """
        Tìm chính xác user theo tên — O(log n).

        Args:
            name (str): tên đầy đủ

        Returns:
            User | None: User nếu tìm thấy, None nếu không
        """
        pass

    def search_prefix(self, prefix: str) -> list[User]:
        """
        Fuzzy search: tìm tất cả user có tên chứa chuỗi prefix.
        Dùng in-order traversal trên AVL + kiểm tra substring — O(n).

        Args:
            prefix (str): chuỗi con cần tìm (VD "Minh" → "Nhật Minh", "Minh Tuấn")

        Returns:
            list[User]: danh sách user khớp, sắp xếp theo tên
        """
        pass

    def inorder(self) -> list[User]:
        """
        Duyệt in-order → danh sách user sắp xếp theo tên A→Z.

        Returns:
            list[User]: danh sách đã sắp xếp
        """
        pass

