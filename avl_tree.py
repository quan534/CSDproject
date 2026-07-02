from models import User
from typing import Optional

class _AVLNode:
    """Node nội bộ của AVL Tree. Key = name (str), value = User object."""
    def __init__(self, key: str, user: User):
        self.key    = key          # tên dùng để so sánh
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
        self._root = None

    # ── INTERNAL HELPERS ──────────────────────────────────────────────

    def _height(self, node: _AVLNode) -> int:
        """Trả về height của node (0 nếu None)."""
        pass

    def _balance_factor(self, node: _AVLNode) -> int:
        """
        Tính balance factor = height(left) - height(right).
        AVL yêu cầu giá trị này luôn trong [-1, 0, 1].
        """
        pass

    def _update_height(self, node: _AVLNode) -> None:
        """Cập nhật lại height sau khi rotate."""
        pass

    def _rotate_right(self, y: _AVLNode) -> _AVLNode:
        """
        Xoay phải tại node y (xử lý trường hợp Left-Left).

        Args:
            y (_AVLNode): node mất cân bằng

        Returns:
            _AVLNode: node gốc mới sau khi xoay
        """
        pass

    def _rotate_left(self, x: _AVLNode) -> _AVLNode:
        """
        Xoay trái tại node x (xử lý trường hợp Right-Right).

        Args:
            x (_AVLNode): node mất cân bằng

        Returns:
            _AVLNode: node gốc mới sau khi xoay
        """
        pass

    def _rebalance(self, node: _AVLNode) -> _AVLNode:
        """
        Kiểm tra balance factor và gọi rotate phù hợp (LL, RR, LR, RL).

        Args:
            node (_AVLNode): node cần kiểm tra

        Returns:
            _AVLNode: node sau khi đã cân bằng
        """
        pass

    def _insert_recursive(self, node: _AVLNode, key: str, user: User) -> _AVLNode:
        """Đệ quy insert + rebalance trên đường về."""
        pass

    def _delete_recursive(self, node: _AVLNode, key: str) -> _AVLNode:
        """Đệ quy delete + rebalance. Dùng in-order successor khi có 2 con."""
        pass

    def _min_node(self, node: _AVLNode) -> _AVLNode:
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
        pass

    def delete(self, name: str) -> None:
        """
        Xóa node có key = name khỏi cây.

        Args:
            name (str): tên của user cần xóa

        Returns:
            None
        """
        pass

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

