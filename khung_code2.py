
class User:
    """
    Đại diện một người dùng trong mạng xã hội.

    Attributes:
        user_id   (str)       : ID duy nhất, dạng "U001"
        name      (str)       : Họ và tên đầy đủ
        age       (int)       : Tuổi (dùng để filter gợi ý)
        location  (str)       : Khu vực / thành phố
        interests (list[str]) : Danh sách sở thích, VD ["music", "travel"]
    """

    def __init__(self, user_id: str, name: str, age: int,
                 location: str, interests: list = None):
        self.user_id   = user_id
        self.name      = name
        self.age       = age
        self.location  = location
        self.interests = interests if interests is not None else []

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, {self.age}, {self.location})"

    def to_dict(self) -> dict:
        """
        Chuyển User thành dict để xuất JSON/CSV.

        Returns:
            dict: {"user_id": ..., "name": ..., "age": ..., ...}
        """
        pass

    @staticmethod
    def from_dict(data: dict) -> "User":
        """
        Tạo User từ dict (dùng khi import file).

        Args:
            data (dict): dict chứa các field của User

        Returns:
            User: object User mới
        """
        pass


# ─────────────────────────────────────────────
#  FILE: avl_tree.py
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  FILE: social_graph.py
# ─────────────────────────────────────────────

from collections import deque


class SocialGraph:
    """
    Đồ thị vô hướng biểu diễn mạng xã hội.
    Dùng Adjacency List (dict of sets) — tối ưu cho sparse graph.

    _adj: dict[str, set[str]]
        key   = user_id
        value = set các user_id đã kết bạn

    Tất cả thuật toán (BFS, DFS, mutual friends) tự implement.
    """

    def __init__(self):
        self._adj: dict[str, set] = {}   # adjacency list chính

    # ── NODE (USER) MANAGEMENT ────────────────────────────────────────

    def add_node(self, user_id: str) -> None:
        """
        Thêm node (user) vào đồ thị khi tạo tài khoản mới.

        Args:
            user_id (str): ID người dùng mới

        Returns:
            None
        """
        pass

    def remove_node(self, user_id: str) -> None:
        """
        Xóa node và tất cả cạnh liên quan khi xóa tài khoản.

        Args:
            user_id (str): ID người dùng cần xóa

        Returns:
            None. Cập nhật adjacency list của tất cả bạn bè cũ.
        """
        pass

    # ── EDGE (FRIENDSHIP) MANAGEMENT ─────────────────────────────────

    def add_edge(self, user_id1: str, user_id2: str) -> None:
        """
        Tạo kết bạn (cạnh 2 chiều) giữa 2 người dùng.

        Args:
            user_id1 (str): ID người dùng 1
            user_id2 (str): ID người dùng 2

        Returns:
            None
        """
        pass

    def remove_edge(self, user_id1: str, user_id2: str) -> None:
        """
        Hủy kết bạn (xóa cạnh 2 chiều).

        Args:
            user_id1 (str): ID người dùng 1
            user_id2 (str): ID người dùng 2

        Returns:
            None
        """
        pass

    def are_friends(self, user_id1: str, user_id2: str) -> bool:
        """
        Kiểm tra 2 người có phải bạn bè không — O(1) nhờ set.

        Args:
            user_id1, user_id2 (str)

        Returns:
            bool
        """
        pass

    def get_friends(self, user_id: str) -> set:
        """
        Lấy tập hợp ID bạn bè của một user — O(1).

        Args:
            user_id (str)

        Returns:
            set[str]: tập ID bạn bè
        """
        pass

    def degree(self, user_id: str) -> int:
        """
        Số bạn bè (bậc của node) — O(1).

        Args:
            user_id (str)

        Returns:
            int: số bạn bè
        """
        pass

    # ── CORE ALGORITHMS (tự implement, không dùng thư viện) ──────────

    def get_mutual_friends(self, user_id1: str, user_id2: str) -> set:
        """
        Tìm bạn chung giữa 2 người dùng — intersection của 2 set — O(min(d1,d2)).

        Args:
            user_id1 (str)
            user_id2 (str)

        Returns:
            set[str]: tập ID bạn chung
        """
        pass

    def get_candidates_at_depth2(self, user_id: str) -> dict:
        """
        BFS độ sâu 2: tìm tất cả "bạn của bạn" chưa kết bạn với user.
        Đây là nguồn dữ liệu thô cho SuggestionEngine.

        Args:
            user_id (str): ID người cần gợi ý

        Returns:
            dict[str, int]: {candidate_id: số_bạn_chung}
            VD: {"U005": 3, "U012": 1}
        """
        pass

    def shortest_path(self, from_id: str, to_id: str) -> list:
        """
        BFS tìm đường đi ngắn nhất (chuỗi kết nối) giữa 2 người.

        Args:
            from_id (str): ID người xuất phát
            to_id   (str): ID người đích

        Returns:
            list[str]: danh sách ID theo đường đi, VD ["U001","U003","U007"]
                       Trả về [] nếu không có đường đi.
        """
        pass

    def degree_of_separation(self, from_id: str, to_id: str) -> int:
        """
        Tính số bậc ngăn cách dựa trên shortest_path.

        Args:
            from_id (str)
            to_id   (str)

        Returns:
            int: số bậc (= len(path) - 1), hoặc -1 nếu không kết nối
        """
        pass

    def find_connected_components(self) -> list:
        """
        DFS/BFS quét toàn đồ thị, phân nhóm thành các connected component
        (các "cộng đồng" tách biệt nhau).

        Returns:
            list[set[str]]: danh sách các nhóm, mỗi nhóm là set user_id
            VD: [{"U001","U002","U003"}, {"U007","U008"}]
        """
        pass

    def get_all_edges(self) -> list:
        """
        Lấy tất cả cạnh (friendship) trong đồ thị (dùng để export / visualize).

        Returns:
            list[tuple[str,str]]: danh sách cặp (id1, id2), mỗi cạnh xuất hiện 1 lần
        """
        pass

    def stats(self) -> dict:
        """
        Thống kê cơ bản của đồ thị.

        Returns:
            dict: {
                "total_nodes": int,
                "total_edges": int,
                "avg_degree" : float,
                "density"    : float,   # = 2E / (V*(V-1))
                "components" : int      # số connected components
            }
        """
        pass


# ─────────────────────────────────────────────
#  FILE: user_manager.py
# ─────────────────────────────────────────────

class UserManager:
    """
    Quản lý toàn bộ người dùng và quan hệ kết bạn.

    Cấu trúc nội bộ:
        _users    (list[User])              : mảng chính, theo yêu cầu đề bài
        _id_map   (dict[str, User])         : tra cứu O(1) theo user_id
        _avl_name (AVLTree)                 : tìm kiếm theo tên O(log n)
        _graph    (SocialGraph)             : đồ thị bạn bè
        _pending  (dict[str, list[FriendRequest]]): pending[to_id] = [requests]
        _blocked  (dict[str, set[str]])     : blocked[user_id] = set bị chặn
    """

    def __init__(self):
        self._users:   list     = []
        self._id_map:  dict     = {}
        self._avl_name = AVLTree()
        self._graph    = SocialGraph()
        self._pending: dict     = {}
        self._blocked: dict     = {}
        self._next_id: int      = 1       # auto-increment ID

    def _generate_id(self) -> str:
        """Sinh user_id mới dạng 'U001', 'U002', ..."""
        pass

    # ── CRUD ──────────────────────────────────────────────────────────

    def add_user(self, name: str, age: int, location: str,
                 interests: list) -> User:
        """
        Tạo và thêm người dùng mới vào hệ thống.
        Đồng thời cập nhật: _users list, _id_map, AVL Tree, SocialGraph.

        Args:
            name      (str)       : Họ tên
            age       (int)       : Tuổi
            location  (str)       : Khu vực
            interests (list[str]) : Danh sách sở thích

        Returns:
            User: object User vừa tạo (kèm user_id được gán)
        """
        pass

    def remove_user(self, user_id: str) -> bool:
        """
        Xóa người dùng và dọn sạch toàn bộ dữ liệu liên quan:
        pending requests, blocked list, graph edges.

        Args:
            user_id (str): ID người dùng cần xóa

        Returns:
            bool: True nếu xóa thành công, False nếu không tồn tại
        """
        pass

    def update_user(self, user_id: str, **kwargs) -> bool:
        """
        Cập nhật thông tin người dùng. Nếu cập nhật name thì rebuild AVL node.

        Args:
            user_id (str) : ID người cần cập nhật
            **kwargs      : Các field cần thay đổi (name, age, location, interests)
                            VD: update_user("U001", age=26, location="HCM")

        Returns:
            bool: True nếu thành công
        """
        pass

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Lấy User theo ID — O(1) qua hash map.

        Args:
            user_id (str)

        Returns:
            User | None
        """
        pass

    def get_all_users(self) -> list:
        """
        Trả về toàn bộ danh sách users (bản copy của _users array).

        Returns:
            list[User]
        """
        pass

    # ── SEARCH ────────────────────────────────────────────────────────

    def search_by_name_exact(self, name: str) -> Optional[User]:
        """
        Tìm kiếm chính xác theo tên qua AVL Tree — O(log n).

        Args:
            name (str): tên đầy đủ

        Returns:
            User | None
        """
        pass

    def search_by_name_fuzzy(self, query: str) -> list:
        """
        Tìm kiếm tương đối (fuzzy): tên chứa chuỗi query (không phân biệt hoa/thường).
        Dùng linear scan trên _users array — O(n).

        Args:
            query (str): chuỗi con, VD "minh" → "Nhật Minh", "Minh Tuấn"

        Returns:
            list[User]: danh sách user khớp
        """
        pass

    def search_by_age_range(self, min_age: int, max_age: int) -> list:
        """
        Tìm user trong khoảng tuổi [min_age, max_age].
        Linear scan trên _users (hoặc build AVL theo age nếu muốn O(log n + k)).

        Args:
            min_age (int)
            max_age (int)

        Returns:
            list[User]: danh sách user trong khoảng tuổi
        """
        pass

    def list_users_sorted(self) -> list:
        """
        Dùng in-order traversal của AVL Tree → danh sách sắp xếp theo tên A→Z.

        Returns:
            list[User]
        """
        pass

    # ── FRIEND REQUEST FLOW ───────────────────────────────────────────

    def send_friend_request(self, from_id: str, to_id: str) -> str:
        """
        Gửi lời mời kết bạn. Kiểm tra: đã bạn? đã pending? bị block?

        Args:
            from_id (str): người gửi
            to_id   (str): người nhận

        Returns:
            str: thông báo kết quả ("sent" / "already_friends" / "blocked" / "already_pending")
        """
        pass

    def cancel_friend_request(self, from_id: str, to_id: str) -> bool:
        """
        Hủy lời mời kết bạn đã gửi (unrequest).

        Args:
            from_id (str)
            to_id   (str)

        Returns:
            bool: True nếu hủy thành công
        """
        pass

    def accept_friend_request(self, user_id: str, from_id: str) -> bool:
        """
        Chấp nhận lời mời → tạo cạnh 2 chiều trong SocialGraph.

        Args:
            user_id (str): người nhận (đang accept)
            from_id (str): người đã gửi request

        Returns:
            bool: True nếu thành công
        """
        pass

    def decline_friend_request(self, user_id: str, from_id: str) -> bool:
        """
        Từ chối lời mời → thêm from_id vào danh sách block của user_id
        (không gợi ý lại người này nữa).

        Args:
            user_id (str): người nhận (đang decline)
            from_id (str): người đã gửi request

        Returns:
            bool: True nếu thành công
        """
        pass

    def unfriend(self, user_id1: str, user_id2: str) -> bool:
        """
        Hủy kết bạn — xóa cạnh trong SocialGraph.

        Args:
            user_id1 (str)
            user_id2 (str)

        Returns:
            bool: True nếu thành công
        """
        pass

    def get_pending_requests(self, user_id: str) -> list:
        """
        Lấy danh sách lời mời kết bạn đang chờ của user.

        Args:
            user_id (str)

        Returns:
            list[FriendRequest]: các request có status = PENDING
        """
        pass

    # ── BLOCK / UNBLOCK ───────────────────────────────────────────────

    def block_user(self, user_id: str, target_id: str) -> bool:
        """
        Chặn người dùng: xóa kết bạn (nếu có), thêm vào blocked set,
        loại khỏi mọi gợi ý và tìm kiếm của nhau.

        Args:
            user_id   (str): người thực hiện block
            target_id (str): người bị block

        Returns:
            bool: True nếu thành công
        """
        pass

    def unblock_user(self, user_id: str, target_id: str) -> bool:
        """
        Bỏ chặn người dùng.

        Args:
            user_id   (str)
            target_id (str)

        Returns:
            bool
        """
        pass

    def is_blocked(self, user_id: str, target_id: str) -> bool:
        """
        Kiểm tra user_id có block target_id không (hoặc ngược lại).

        Args:
            user_id   (str)
            target_id (str)

        Returns:
            bool: True nếu một trong hai đã block nhau
        """
        pass

    def get_graph(self) -> SocialGraph:
        """Trả về SocialGraph để các module khác dùng."""
        return self._graph


# ─────────────────────────────────────────────
#  FILE: data_manager.py
# ─────────────────────────────────────────────

import json
import csv
import random
import time


class DataManager:
    """
    Import/Export dữ liệu và sinh dữ liệu mẫu để demo.
    """

    SAMPLE_NAMES     = ["An", "Bình", "Chi", "Duy", "Em", "Phong", "Giang",
                        "Hà", "Ivy", "Khánh", "Lan", "Minh", "Nam", "Oanh"]
    SAMPLE_LOCATIONS = ["HCM", "HN", "ĐN", "Cần Thơ", "Huế"]
    SAMPLE_INTERESTS = ["music", "travel", "gaming", "cooking", "sports",
                        "reading", "photography", "coding", "movies", "art"]

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    def export_json(self, filepath: str) -> bool:
        """
        Xuất toàn bộ dữ liệu (users + friendships) ra file JSON.

        Args:
            filepath (str): đường dẫn file output, VD "data/network.json"

        Returns:
            bool: True nếu xuất thành công

        Output format:
            {
                "users": [ {user fields...}, ... ],
                "friendships": [ [id1, id2], ... ],
                "exported_at": "ISO timestamp"
            }
        """
        pass

    def import_json(self, filepath: str) -> dict:
        """
        Nạp dữ liệu từ file JSON, rebuild toàn bộ cấu trúc dữ liệu.

        Args:
            filepath (str): đường dẫn file input

        Returns:
            dict: {"users_loaded": int, "friendships_loaded": int}
        """
        pass

    def export_csv(self, users_filepath: str, edges_filepath: str) -> bool:
        """
        Xuất ra 2 file CSV riêng: một cho users, một cho edges.

        Args:
            users_filepath (str): VD "data/users.csv"
            edges_filepath (str): VD "data/edges.csv"

        Returns:
            bool: True nếu xuất thành công
        """
        pass

    def import_csv(self, users_filepath: str, edges_filepath: str) -> dict:
        """
        Nạp dữ liệu từ 2 file CSV (users + edges).

        Args:
            users_filepath (str)
            edges_filepath (str)

        Returns:
            dict: {"users_loaded": int, "friendships_loaded": int}
        """
        pass

    def generate_sample_data(self, num_users: int = 50,
                              avg_friends: int = 5,
                              seed: int = 42) -> dict:
        """
        Sinh ngẫu nhiên num_users người dùng và kết bạn để demo.
        Dùng seed để tái tạo cùng dữ liệu khi cần.

        Args:
            num_users   (int): số người dùng cần sinh (default 50, demo 10000)
            avg_friends (int): số bạn bè trung bình mỗi người
            seed        (int): random seed

        Returns:
            dict: {"users_created": int, "friendships_created": int, "time_ms": float}
        """
        pass


