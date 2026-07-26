import unicodedata
from models import User

def _normalize_name(name: str) -> str:
    """Chuẩn hóa tiếng Việt (NFC), xóa khoảng trắng thừa và đưa về chữ thường."""
    if not name:
        return ""
    return unicodedata.normalize('NFC', name).strip().lower()

def _get_sort_key_name_first(user: User):
    """
    Tạo Key sắp xếp ưu tiên:
    1. Tên chính (từ cuối cùng)
    2. Họ và tên lót (các từ phía trước)
    3. ID người dùng (để đảm bảo tính duy nhất và ổn định)
    """
    normalized = _normalize_name(user.name)
    parts = normalized.split()
    
    if not parts:
        return ("", "", str(user.user_id))
    
    first_name = parts[-1]                      # Tên chính (VD: "an", "bình")
    middle_and_last = " ".join(parts[:-1])        # Họ và tên lót (VD: "nguyễn văn")
    
    return (first_name, middle_and_last, str(user.user_id))

def extract_last_name(full_name: str) -> str:
    """ Trích xuất từ cuối cùng của họ tên và chuẩn hóa chữ thường """
    if not full_name:
        return ""
    # Đồng nhất bảng mã dấu tiếng Việt (NFC) và chuyển về chữ thường
    clean_name = unicodedata.normalize('NFC', full_name).strip().lower()
    words = clean_name.split()
    return words[-1] if words else ""



class AVLNode:
    def __init__(self, user: User):
        self.key_name = extract_last_name(user.name)  # Khóa là Tên chung (ví dụ: "an")
        self.users = [user]                           # Mảng lưu các đối tượng trùng tên chính
        self.left = None
        self.right = None
        self.height = 1



class AVLTree:
    def __init__(self):
        self.root = None

    # --- Các hàm bổ trợ quản lý chiều cao và xoay cây ---
    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        # Thực hiện xoay
        y.right = z
        z.left = T3
        
        # Cập nhật chiều cao
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        # Thực hiện xoay
        y.left = z
        z.right = T2
        
        # Cập nhật chiều cao
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _get_min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _balance_node(self, node):
        """ Hàm trung tâm: Tự động tính độ lệch và xoay cân bằng cây """
        if not node:
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Trường hợp LỆCH TRÁI (Left Heavy)
        if balance > 1:
            if self._get_balance(node.left) < 0:
                node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Trường hợp LỆCH PHẢI (Right Heavy)
        if balance < -1:
            if self._get_balance(node.right) > 0:
                node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node


    def insert(self, user: User):
        self.root = self._insert_recursive(self.root, user)

    def _insert_recursive(self, node, user: User):
        if not node:
            return AVLNode(user)

        target_key = extract_last_name(user.name)

        if target_key < node.key_name:
            node.left = self._insert_recursive(node.left, user)
        elif target_key > node.key_name:
            node.right = self._insert_recursive(node.right, user)
        else:
            # Gặp người trùng tên chính: Chỉ thêm đối tượng vào mảng có sẵn
            node.users.append(user)
            return node

        return self._balance_node(node)


    def delete(self, full_name: str, user_id: int):
        self.root = self._delete_recursive(self.root, full_name, user_id)
    
    def _delete_successor(self, node, key_name):
        if node is None:
            return None

        if key_name < node.key_name:
            node.left = self._delete_successor(node.left, key_name)

        elif key_name > node.key_name:
            node.right = self._delete_successor(node.right, key_name)

        else:
            # Node chỉ có 0 hoặc 1 con
            if node.left is None:
                return node.right

            if node.right is None:
                return node.left

            # Trường hợp rất hiếm:
            # successor cũng có 2 con
            next_successor = self._get_min_value_node(node.right)

            node.key_name = next_successor.key_name
            node.users = next_successor.users.copy()

            node.right = self._delete_successor(
            node.right,
            next_successor.key_name
            )

        return self._balance_node(node)

    def _delete_recursive(self, node, full_name: str, user_id: int):
        if not node:
            return node

        target_key = extract_last_name(full_name)

        if target_key < node.key_name:
            node.left = self._delete_recursive(node.left, full_name, user_id)
        elif target_key > node.key_name:
            node.right = self._delete_recursive(node.right, full_name, user_id)
        else:
            # Tìm thấy Node chứa nhóm người có tên cần xóa
            # Bước 2.1: Duyệt tìm đúng User có ID trùng khớp trong mảng để xóa
            for u in node.users:
                if u.user_id == user_id:
                    node.users.remove(u)
                    break

            # Bước 2.2: Nếu mảng vẫn còn người trùng tên khác -> Giữ nguyên Node trên cây
            if len(node.users) > 0:
                return node

            # Bước 2.3: Mảng trống rỗng -> Tiến hành xóa Node này khỏi cấu trúc cây AVL
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            temp = self._get_min_value_node(node.right)

            # Sao chép dữ liệu của node thế mạng
            node.key_name = temp.key_name
            node.users = temp.users.copy()

            # Xóa toàn bộ node thế mạng
            node.right = self._delete_successor(node.right,temp.key_name)
           

        return self._balance_node(node)

    
    def inorder(self) -> list[User]:
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if not node:
            return
        self._inorder_recursive(node.left, result)
        result.extend(node.users)  # Đổ toàn bộ danh sách đối tượng tại node này vào kết quả
        self._inorder_recursive(node.right, result)
        
    def search_exact(self, full_name: str) -> list:
        
        if not self.root or not full_name:
            return []
 
        target_key = extract_last_name(full_name)
        normalized_full_name = unicodedata.normalize('NFC', full_name).strip().lower()
 
        current = self.root
        while current:
            if target_key < current.key_name:
                current = current.left
            elif target_key > current.key_name:
                current = current.right
            else:
                return [
                    u for u in current.users
                    if unicodedata.normalize('NFC', u.name).strip().lower() == normalized_full_name
                ]
        return []

    def update_user(self, old_full_name: str, user_id: int, new_name: str = None, new_age: int = None):
        if not self.root:
            return

        target_key = extract_last_name(old_full_name)
        current = self.root
        target_user = None

        # Tìm kiếm nhị phân để định vị nhanh Node chứa tên cũ
        while current:
            if target_key < current.key_name:
                current = current.left
            elif target_key > current.key_name:
                current = current.right
            else:
                for u in current.users:
                    if u.user_id == user_id:
                        target_user = u
                        break
                break

        if not target_user:
            return

        # Sửa thông tin phụ (Tuổi)
        if new_age is not None:
            target_user.age = new_age

        # Sửa thông tin định tuyến (Họ tên)
        if new_name is not None:
            # Quy trình an toàn tuyệt đối cho cây: Xóa ở vị trí cũ -> Đổi tên -> Chèn lại vào vị trí mới
            self.delete(old_full_name, user_id)
            target_user.name = new_name
            self.insert(target_user)
        
        


