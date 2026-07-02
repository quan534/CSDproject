"""
=============================================================================
  SOCIAL NETWORK FRIEND SUGGESTION SYSTEM
  Skeleton / Blueprint — chỉ gồm class, method signatures, docstrings
=============================================================================

CẤU TRÚC DỮ LIỆU SỬ DỤNG:
  - List/Array      : lưu danh sách users tổng (UserManager._users)
  - AVL Tree        : tìm kiếm user theo name O(log n) (AVLTree)
  - Hash Map (dict) : tra cứu O(1) theo user_id (UserManager._id_map)
  - Graph (Adj List): mô hình mạng xã hội (SocialGraph)
  - Max-Heap        : xếp hạng gợi ý theo mutual count (heapq)
  - Queue (deque)   : BFS cho shortest path, community detection

MODULES:
  1. models.py          → User, FriendRequest
  2. avl_tree.py        → AVLTree (tự cân bằng, thay BST thuần)
  3. social_graph.py    → SocialGraph (adjacency list, tất cả thuật toán đồ thị)
  4. user_manager.py    → UserManager (CRUD, block, search, pending requests)
  5. suggestion_engine.py → SuggestionEngine (gợi ý, filter, scoring)
  6. network_analytics.py → NetworkAnalytics (BFS path, influencer, community)
  7. data_manager.py    → DataManager (import/export JSON/CSV, generate fake data)
  8. visualizer.py      → Visualizer (PyVis render — chỉ gọi sau khi tính xong)
  9. cli_shell.py       → CLIShell (interactive command shell)
  10. main.py           → Entry point

=============================================================================
"""

# ─────────────────────────────────────────────
#  FILE: models.py
# ─────────────────────────────────────────────

from typing import Optional
from enum import Enum


class RequestStatus(Enum):
    PENDING  = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


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
        # return một dict với keys, values tương ứng là tên các attributes và giá trị của nó của của đối tượng user
        return {"user_id": self.user_id, "name": self.name, "age": self.age, "location": self.location, "interests": self.interests}

        pass

    @staticmethod
    def from_dict(data: dict) -> "User":
        # Tạo User từ dict (dùng khi import file).
        return User(data["user_id"],data["name"],data["age"],data["location"],data["interests"])
        pass


class FriendRequest:
    """
    Đại diện một lời mời kết bạn.

    Attributes:
        from_id   (str)          : ID người gửi
        to_id     (str)          : ID người nhận
        status    (RequestStatus): PENDING / ACCEPTED / DECLINED
        timestamp (float)        : Unix timestamp lúc gửi
    """

    def __init__(self, from_id: str, to_id: str,
                 status: RequestStatus = RequestStatus.PENDING,
                 timestamp: float = 0.0):
        self.from_id   = from_id
        self.to_id     = to_id
        self.status    = status
        self.timestamp = timestamp

    def __repr__(self):
        return f"FriendRequest({self.from_id} → {self.to_id}, {self.status.value})"


class SuggestionResult:
    """
    Kết quả một gợi ý kết bạn (dùng để hiển thị cho người dùng).

    Attributes:
        user          (User)      : Người được gợi ý
        mutual_count  (int)       : Số bạn chung
        mutual_names  (list[str]) : Tên các bạn chung (để hiển thị lý do)
        common_interests (list[str]): Sở thích chung
        score         (float)     : Điểm tổng hợp (mutual + interest bonus)
    """

    def __init__(self, user: User, mutual_count: int,
                 mutual_names: list = None,
                 common_interests: list = None,
                 score: float = 0.0):
        self.user             = user
        self.mutual_count     = mutual_count
        self.mutual_names     = mutual_names     if mutual_names     is not None else []
        self.common_interests = common_interests if common_interests is not None else []
        self.score            = score

    def __repr__(self):
        return f"SuggestionResult({self.user.name}, mutual={self.mutual_count}, score={self.score})"


class FilterCriteria:
    """
    Bộ lọc cho danh sách gợi ý. None = bỏ qua tiêu chí đó.

    Attributes:
        age_range      (tuple|None) : (min_age, max_age), VD (18, 25)
        location       (str|None)   : Lọc theo khu vực chính xác
        interests      (list|None)  : Lọc user có ÍT NHẤT 1 sở thích chung
        min_mutual     (int)        : Số bạn chung tối thiểu (mặc định 0)
    """

    def __init__(self, age_range: Optional[tuple] = None,
                 location: Optional[str] = None,
                 interests: Optional[list] = None,
                 min_mutual: int = 0):
        self.age_range  = age_range
        self.location   = location
        self.interests  = interests
        self.min_mutual = min_mutual

    def __repr__(self):
        return (f"FilterCriteria(age={self.age_range}, location={self.location}, "
                f"interests={self.interests}, min_mutual={self.min_mutual})")


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
        if user_id not in self._adj:
            self._adj[user_id] = set()
 
    def remove_node(self, user_id: str) -> None:
        """
        Xóa node và tất cả cạnh liên quan khi xóa tài khoản.
 
        Args:
            user_id (str): ID người dùng cần xóa
 
        Returns:
            None. Cập nhật adjacency list của tất cả bạn bè cũ.
        """
        if user_id not in self._adj:
            return
        # Gỡ user_id khỏi danh sách bạn bè của tất cả người từng kết bạn
        for friend_id in self._adj[user_id]:
            self._adj[friend_id].discard(user_id)
        # Xóa hẳn node
        del self._adj[user_id]
 
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
        if user_id1 == user_id2:
            return  # không tự kết bạn với chính mình
        # Đảm bảo cả 2 node tồn tại
        self.add_node(user_id1)
        self.add_node(user_id2)
        self._adj[user_id1].add(user_id2)
        self._adj[user_id2].add(user_id1)
 
    def remove_edge(self, user_id1: str, user_id2: str) -> None:
        """
        Hủy kết bạn (xóa cạnh 2 chiều).
 
        Args:
            user_id1 (str): ID người dùng 1
            user_id2 (str): ID người dùng 2
 
        Returns:
            None
        """
        if user_id1 in self._adj:
            self._adj[user_id1].discard(user_id2)
        if user_id2 in self._adj:
            self._adj[user_id2].discard(user_id1)
 
    def are_friends(self, user_id1: str, user_id2: str) -> bool:
        """
        Kiểm tra 2 người có phải bạn bè không — O(1) nhờ set.
 
        Args:
            user_id1, user_id2 (str)
 
        Returns:
            bool
        """
        return user_id2 in self._adj.get(user_id1, set())
 
    def get_friends(self, user_id: str) -> set:
        """
        Lấy tập hợp ID bạn bè của một user — O(1).
 
        Args:
            user_id (str)
 
        Returns:
            set[str]: tập ID bạn bè
        """
        # Trả về bản copy để tránh bên ngoài chỉnh sửa trực tiếp _adj
        return set(self._adj.get(user_id, set()))
 
    def degree(self, user_id: str) -> int:
        """
        Số bạn bè (bậc của node) — O(1).
 
        Args:
            user_id (str)
 
        Returns:
            int: số bạn bè
        """
        return len(self._adj.get(user_id, set()))
 
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
        friends1 = self._adj.get(user_id1, set())
        friends2 = self._adj.get(user_id2, set())
        return friends1 & friends2
 
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
        if user_id not in self._adj:
            return {}
 
        direct_friends = self._adj[user_id]
        candidates: dict = {}
 
        # Với mỗi bạn trực tiếp (depth 1), xét bạn của bạn đó (depth 2)
        for friend_id in direct_friends:
            for fof_id in self._adj.get(friend_id, set()):
                # Loại: chính user_id, và những người đã là bạn trực tiếp
                if fof_id == user_id or fof_id in direct_friends:
                    continue
                candidates[fof_id] = candidates.get(fof_id, 0) + 1
 
        return candidates
 
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
        if from_id not in self._adj or to_id not in self._adj:
            return []
 
        if from_id == to_id:
            return [from_id]
 
        visited = {from_id}
        parent = {from_id: None}
        queue = deque([from_id])
 
        found = False
        while queue:
            current = queue.popleft()
            if current == to_id:
                found = True
                break
            for neighbor in self._adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
 
        if not found and to_id not in visited:
            return []
 
        # Truy ngược từ to_id về from_id qua parent map
        path = []
        node = to_id
        while node is not None:
            path.append(node)
            node = parent.get(node)
        path.reverse()
 
        # Nếu node đầu của path không phải from_id thì coi như không tìm được
        if not path or path[0] != from_id:
            return []
 
        return path
 
    def degree_of_separation(self, from_id: str, to_id: str) -> int:
        """
        Tính số bậc ngăn cách dựa trên shortest_path.
 
        Args:
            from_id (str)
            to_id   (str)
 
        Returns:
            int: số bậc (= len(path) - 1), hoặc -1 nếu không kết nối
        """
        path = self.shortest_path(from_id, to_id)
        if not path:
            return -1
        return len(path) - 1
 
    def find_connected_components(self) -> list:
        """
        DFS/BFS quét toàn đồ thị, phân nhóm thành các connected component
        (các "cộng đồng" tách biệt nhau).
 
        Returns:
            list[set[str]]: danh sách các nhóm, mỗi nhóm là set user_id
            VD: [{"U001","U002","U003"}, {"U007","U008"}]
        """
        visited = set()
        components = []
 
        for start_node in self._adj:
            if start_node in visited:
                continue
 
            # BFS từ start_node để lấy toàn bộ component chứa nó
            component = set()
            queue = deque([start_node])
            visited.add(start_node)
 
            while queue:
                current = queue.popleft()
                component.add(current)
                for neighbor in self._adj[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
 
            components.append(component)
 
        return components
 
    def get_all_edges(self) -> list:
        """
        Lấy tất cả cạnh (friendship) trong đồ thị (dùng để export / visualize).
 
        Returns:
            list[tuple[str,str]]: danh sách cặp (id1, id2), mỗi cạnh xuất hiện 1 lần
        """
        edges = []
        seen = set()
 
        for node, neighbors in self._adj.items():
            for neighbor in neighbors:
                # Dùng frozenset để tránh đếm cạnh 2 lần (A-B và B-A)
                edge_key = frozenset((node, neighbor))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append((node, neighbor))
 
        return edges
 
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
        total_nodes = len(self._adj)
        total_edges = len(self.get_all_edges())
 
        avg_degree = (2 * total_edges / total_nodes) if total_nodes > 0 else 0.0
 
        if total_nodes > 1:
            density = (2 * total_edges) / (total_nodes * (total_nodes - 1))
        else:
            density = 0.0
 
        components = len(self.find_connected_components())
 
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "avg_degree": avg_degree,
            "density": density,
            "components": components,
        }


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
#  FILE: suggestion_engine.py
# ─────────────────────────────────────────────

import heapq


class SuggestionEngine:
    """
    Lõi thuật toán gợi ý kết bạn.

    Chiến lược scoring (weighted):
        score = mutual_count * W_MUTUAL + common_interests * W_INTEREST
        W_MUTUAL   = 1.0  (trọng số bạn chung)
        W_INTEREST = 0.5  (trọng số sở thích chung)
    """

    W_MUTUAL   = 1.0
    W_INTEREST = 0.5

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    def _compute_score(self, user: User, candidate: User,
                       mutual_count: int) -> float:
        """
        Tính điểm tổng hợp cho một gợi ý.

        Args:
            user         (User): người đang được gợi ý cho
            candidate    (User): người được gợi ý
            mutual_count (int) : số bạn chung đã tính

        Returns:
            float: điểm tổng hợp
        """
        pass

    def _apply_filters(self, user: User, candidates: list,
                       filters: FilterCriteria) -> list:
        """
        Áp dụng FilterCriteria lên danh sách SuggestionResult.
        Lọc theo: age_range, location, interests, min_mutual.

        Args:
            user       (User)            : người dùng hiện tại
            candidates (list[SuggestionResult]): danh sách thô
            filters    (FilterCriteria)  : tiêu chí lọc

        Returns:
            list[SuggestionResult]: danh sách đã lọc
        """
        pass

    def suggest(self, user_id: str, top_k: int = 10,
                filters: FilterCriteria = None) -> list:
        """
        Gợi ý bạn bè cho user_id.

        Thuật toán:
            1. Dùng SocialGraph.get_candidates_at_depth2() → dict{id: mutual_count}
            2. Loại bỏ user bị block (từ cả 2 chiều)
            3. Tính score tổng hợp cho mỗi candidate
            4. Dùng Max-Heap (heapq) lấy top_k — O(n log k)
            5. Áp dụng filters nếu có
            6. Đính kèm mutual_names và common_interests vào kết quả

        Args:
            user_id  (str)                  : ID người cần gợi ý
            top_k    (int)                  : số gợi ý tối đa trả về
            filters  (FilterCriteria | None): bộ lọc tùy chọn

        Returns:
            list[SuggestionResult]: sắp xếp giảm dần theo score
        """
        pass

    def suggest_by_interest_only(self, user_id: str, top_k: int = 10) -> list:
        """
        Gợi ý dựa thuần túy trên sở thích chung (không cần bạn chung).
        Dùng khi user mới, chưa có bạn bè nào.

        Args:
            user_id (str)
            top_k   (int)

        Returns:
            list[SuggestionResult]: sắp xếp theo số sở thích chung giảm dần
        """
        pass


# ─────────────────────────────────────────────
#  FILE: network_analytics.py
# ─────────────────────────────────────────────

class NetworkAnalytics:
    """
    Phân tích mạng lưới nâng cao.
    Mọi thuật toán đều tự implement, gọi vào SocialGraph.
    """

    def __init__(self, user_manager: UserManager):
        self._um    = user_manager
        self._graph = user_manager.get_graph()

    def shortest_path(self, from_id: str, to_id: str) -> dict:
        """
        Tìm đường kết nối ngắn nhất giữa 2 người (dùng BFS trong SocialGraph).

        Args:
            from_id (str)
            to_id   (str)

        Returns:
            dict: {
                "path"      : list[str],  # danh sách user_id
                "path_names": list[str],  # danh sách tên tương ứng
                "degree"    : int         # số bậc ngăn cách
            }
            Trả về {"path": [], "degree": -1} nếu không kết nối.
        """
        pass

    def top_influencers(self, top_n: int = 5) -> list:
        """
        Tìm top N người có nhiều bạn bè nhất (node degree cao nhất).
        Dùng partial sort / Max-Heap — O(V log top_n).

        Args:
            top_n (int): số người muốn lấy

        Returns:
            list[dict]: [{"user": User, "friend_count": int}, ...]
                        sắp xếp giảm dần theo friend_count
        """
        pass

    def detect_communities(self) -> list:
        """
        Phát hiện cộng đồng (Connected Components) bằng BFS/DFS.
        Mỗi component là một "nhóm bạn" tách biệt.

        Returns:
            list[dict]: [
                {
                    "community_id": int,
                    "size"        : int,
                    "members"     : list[User]
                },
                ...
            ]
            Sắp xếp giảm dần theo size.
        """
        pass

    def network_stats(self) -> dict:
        """
        Thống kê tổng quan toàn mạng lưới.

        Returns:
            dict: {
                "total_users"      : int,
                "total_friendships": int,
                "avg_friends"      : float,
                "density"          : float,  # tỉ lệ cạnh thực / cạnh tối đa
                "num_communities"  : int,
                "largest_community": int,    # size of largest component
                "isolated_users"   : int     # số user không có bạn nào
            }
        """
        pass

    def common_interest_score(self, user_id1: str, user_id2: str) -> dict:
        """
        Tính độ tương đồng sở thích giữa 2 người dùng.

        Args:
            user_id1 (str)
            user_id2 (str)

        Returns:
            dict: {
                "common"  : list[str],  # sở thích chung
                "score"   : float,      # Jaccard similarity = |A∩B| / |A∪B|
                "user1_only": list[str],
                "user2_only": list[str]
            }
        """
        pass


# ─────────────────────────────────────────────
#  FILE: data_manager.py
# ─────────────────────────────────────────────

import json
import csv
import random
import time
import datetime


class DataManager:
    """
    Quản lý Import / Export dữ liệu và sinh dữ liệu mẫu.

    Chức năng:
    - Export JSON
    - Import JSON
    - Export CSV
    - Import CSV
    - Generate Sample Data
    """

    SAMPLE_NAMES = [
        "An","Bình","Chi","Duy","Em","Phong","Giang","Hà","Ivy","Khánh",
        "Lan","Minh","Nam","Oanh","Quang","Sơn","Trang","Tuấn","Vy","Yến"
    ]

    SAMPLE_LOCATIONS = [
        "HCM",
        "HN",
        "Đà Nẵng",
        "Huế",
        "Cần Thơ",
        "Hải Phòng",
        "Bình Dương"
    ]

    SAMPLE_INTERESTS = [
        "music",
        "travel",
        "gaming",
        "coding",
        "movies",
        "sports",
        "reading",
        "photography",
        "cooking",
        "art"
    ]

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    # ==========================================================
    # EXPORT JSON
    # ==========================================================

    def export_json(self, filepath: str) -> bool:

        try:

            users = self._um.get_all_users()
            users_data = [u.to_dict() for u in users]
            graph = self._um.get_graph()

            data = {
                "users": users_data,
                "friendships": graph.get_all_edges(),
                "exported_at": datetime.now().isoformat()
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            return True

        except Exception as e:
            print("Export JSON Error:", e)
            return False

    # ==========================================================
    # IMPORT JSON
    # ==========================================================
    def import_json(self, filepath: str) ->dict:

        try:

            with open(filepath,"r",encoding="utf-8") as f:

                data=json.load(f)

            users_loaded=0

            friendships_loaded=0

            # -----------------------------
            # Xóa dữ liệu cũ
            # -----------------------------

            self._um._users.clear()

            self._um._id_map.clear()

            self._um._graph = SocialGraph()

            self._um._avl_name = AVLTree()

            max_id=0

            # -----------------------------
            # Load Users
            # -----------------------------

            for info in data.get("users",[]):

                user=User.from_dict(info)

                self._um._users.append(user)

                self._um._id_map[user.user_id]=user

                self._um._avl_name.insert(user)

                self._um._graph.add_node(user.user_id)

                users_loaded+=1

                try:

                    number=int(user.user_id[1:])

                    if number>max_id:

                        max_id=number

                except ValueError:

                    pass

            # -----------------------------
            # Update next id
            # -----------------------------

            self._um._next_id=max_id+1

            # -----------------------------
            # Load Friendships
            # -----------------------------

            for edge in data.get("friendships",[]):

                if len(edge)!=2:

                    continue

                id1,id2=edge

                if id1 in self._um._id_map and id2 in self._um._id_map:

                    if not self._um._graph.are_friends(id1,id2):

                        self._um._graph.add_edge(id1,id2)

                        friendships_loaded+=1

            return {

                "users_loaded":users_loaded,

                "friendships_loaded":friendships_loaded

            }

        except Exception as e:

            print("Import JSON Error:",e)

            return {

                "users_loaded":0,

                "friendships_loaded":0

            }
    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_csv(self,
                   users_filepath: str,
                   edges_filepath: str) -> bool:

        try:

            users = self._um.get_all_users()

            with open(users_filepath,
                      "w",
                      newline="",
                      encoding="utf-8") as f:

                writer = csv.writer(f)

                writer.writerow([
                    "user_id",
                    "name",
                    "age",
                    "location",
                    "interests"
                ])

                for user in users:

                    writer.writerow([

                        user.user_id,

                        user.name,

                        user.age,

                        user.location,

                        ";".join(user.interests)

                    ])

            graph = self._um.get_graph()

            with open(edges_filepath,
                      "w",
                      newline="",
                      encoding="utf-8") as f:

                writer = csv.writer(f)

                writer.writerow([

                    "user_id1",

                    "user_id2"

                ])

                for id1, id2 in graph.get_all_edges():

                    writer.writerow([id1, id2])

            return True

        except Exception as e:

            print("Export CSV Error:", e)

            return False

    # ==========================================================
    # IMPORT CSV
    # ==========================================================

    def import_csv(self,
                   users_filepath: str,
                   edges_filepath: str) -> dict:

        try:

            users_loaded = 0

            friendships_loaded = 0

            # ----------------------------------
            # Reset toàn bộ dữ liệu cũ
            # ----------------------------------

            self._um._users.clear()

            self._um._id_map.clear()

            self._um._graph = SocialGraph()

            self._um._avl_name = AVLTree()

            max_id = 0

            # ----------------------------------
            # Load Users
            # ----------------------------------

            with open(users_filepath,
                      "r",
                      encoding="utf-8") as f:

                reader = csv.DictReader(f)

                for row in reader:

                    interests = []

                    if row["interests"] != "":

                        interests = row["interests"].split(";")

                    user = User(

                        row["user_id"],

                        row["name"],

                        int(row["age"]),

                        row["location"],

                        interests

                    )

                    self._um._users.append(user)

                    self._um._id_map[user.user_id] = user

                    self._um._avl_name.insert(user)

                    self._um._graph.add_node(user.user_id)

                    users_loaded += 1

                    try:

                        number = int(user.user_id[1:])

                        if number > max_id:

                            max_id = number

                    except ValueError:

                        pass

            self._um._next_id = max_id + 1

            # ----------------------------------
            # Load Friendships
            # ----------------------------------

            with open(edges_filepath,
                      "r",
                      encoding="utf-8") as f:

                reader = csv.DictReader(f)

                for row in reader:

                    id1 = row["user_id1"]

                    id2 = row["user_id2"]

                    if id1 not in self._um._id_map:

                        continue

                    if id2 not in self._um._id_map:

                        continue

                    if not self._um._graph.are_friends(id1, id2):

                        self._um._graph.add_edge(id1, id2)

                        friendships_loaded += 1

            return {

                "users_loaded": users_loaded,

                "friendships_loaded": friendships_loaded

            }

        except Exception as e:

            print("Import CSV Error:", e)

            return {

                "users_loaded": 0,

                "friendships_loaded": 0

            }
    # ==========================================================
    # GENERATE SAMPLE DATA
    # ==========================================================

    def generate_sample_data(self,
                             num_users: int = 50,
                             avg_friends: int = 5,
                             seed: int = 42) -> dict:

        """
        Sinh dữ liệu mẫu.

        Args:
            num_users (int): số lượng user
            avg_friends (int): số bạn trung bình
            seed (int): random seed

        Returns:
            dict
        """

        random.seed(seed)

        start_time = time.time()

        users_created = 0

        friendships_created = 0

        users = []

        last_names = [

            "Nguyễn",

            "Trần",

            "Lê",

            "Phạm",

            "Huỳnh",

            "Phan",

            "Hoàng",

            "Võ"

        ]

        middle_names = [

            "Văn",

            "Thị",

            "Minh",

            "Ngọc",

            "Đăng",

            "Anh",

            "Gia"

        ]

        # ------------------------------------------
        # Generate Users
        # ------------------------------------------

        for _ in range(num_users):

            fullname = "{} {} {}".format(

                random.choice(last_names),

                random.choice(middle_names),

                random.choice(self.SAMPLE_NAMES)

            )

            age = random.randint(18, 60)

            location = random.choice(self.SAMPLE_LOCATIONS)

            interests = random.sample(

                self.SAMPLE_INTERESTS,

                random.randint(2, 5)

            )

            user = self._um.add_user(

                name=fullname,

                age=age,

                location=location,

                interests=interests

            )

            if user is not None:

                users.append(user)

                users_created += 1

        # ------------------------------------------
        # Generate Friendships
        # ------------------------------------------

        graph = self._um.get_graph()

        total_edges = int(num_users * avg_friends / 2)

        max_edges = num_users * (num_users - 1) // 2

        total_edges = min(total_edges, max_edges)

        attempts = 0

        max_attempts = total_edges * 10

        while friendships_created < total_edges and attempts < max_attempts:

            attempts += 1

            user1, user2 = random.sample(users, 2)

            if user1.user_id == user2.user_id:

                continue

            if graph.are_friends(user1.user_id, user2.user_id):

                continue

            graph.add_edge(

                user1.user_id,

                user2.user_id

            )

            friendships_created += 1

        end_time = time.time()

        return {

            "users_created": users_created,

            "friendships_created": friendships_created,

            "execution_time_ms":

                round(

                    (end_time - start_time) * 1000,

                    2

                )

        }

    # ==========================================================
    # RESET DATA
    # ==========================================================

    def clear_data(self):

        """
        Xóa toàn bộ dữ liệu hệ thống.
        """

        self._um._users.clear()

        self._um._id_map.clear()

        self._um._graph = SocialGraph()

        self._um._avl_name = AVLTree()

        self._um._next_id = 1

    # ==========================================================
    # DATA STATISTICS
    # ==========================================================

    def statistics(self):

        """
        Trả về thống kê dữ liệu.
        """

        graph = self._um.get_graph()

        return {
            "total_users": len(self._um.get_all_users()),
            "total_friendships": len(graph.get_all_edges())
        }


# ─────────────────────────────────────────────
#  FILE: visualizer.py
# ─────────────────────────────────────────────

class Visualizer:
    """
    Render mạng lưới quan hệ bằng PyVis (interactive HTML).
    Chỉ đảm nhiệm phần HIỂN THỊ — mọi dữ liệu đã được tính bởi SocialGraph.

    PyVis tạo file HTML có thể mở trên browser, hỗ trợ zoom/drag node.
    """

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    def render_full_network(self, output_path: str = "network.html",
                            highlight_ids: list = None) -> str:
        """
        Vẽ toàn bộ mạng lưới quan hệ.
        Node = user (màu theo location), Edge = friendship.
        Node được highlight nếu có trong highlight_ids.

        Args:
            output_path   (str)       : đường dẫn file HTML output
            highlight_ids (list[str]) : danh sách user_id cần tô màu đặc biệt

        Returns:
            str: đường dẫn file HTML đã tạo
        """
        pass

    def render_ego_network(self, user_id: str,
                           output_path: str = "ego_network.html") -> str:
        """
        Vẽ mạng lưới cá nhân (ego network): user + toàn bộ bạn bè
        + bạn của bạn (depth 2).

        Args:
            user_id     (str): trung tâm của ego network
            output_path (str)

        Returns:
            str: đường dẫn file HTML
        """
        pass

    def render_path(self, path_ids: list,
                    output_path: str = "path.html") -> str:
        """
        Highlight đường đi ngắn nhất giữa 2 người trên đồ thị.

        Args:
            path_ids    (list[str]): danh sách user_id trên đường đi
            output_path (str)

        Returns:
            str: đường dẫn file HTML
        """
        pass

    def render_communities(self, communities: list,
                           output_path: str = "communities.html") -> str:
        """
        Mỗi community được tô một màu khác nhau.

        Args:
            communities (list[dict]): output của NetworkAnalytics.detect_communities()
            output_path (str)

        Returns:
            str: đường dẫn file HTML
        """
        pass


# ─────────────────────────────────────────────
#  FILE: cli_shell.py
# ─────────────────────────────────────────────

class CLIShell:
    """
    Interactive Command-Line Shell.
    Thay vì menu số, dùng lệnh text giống terminal thực:

    COMMANDS (nhóm theo chức năng):
    ─── USER MANAGEMENT ───────────────────────────────
      user add <name> <age> <location> <interest1,interest2,...>
      user remove <id>
      user update <id> <field> <value>
      user get <id>
      user list
      user search <query>          ← fuzzy search theo tên
      user search-age <min> <max>  ← tìm theo khoảng tuổi

    ─── FRIEND MANAGEMENT ─────────────────────────────
      friend request <from_id> <to_id>
      friend cancel  <from_id> <to_id>
      friend accept  <user_id> <from_id>
      friend decline <user_id> <from_id>
      friend remove  <id1> <id2>
      friend list    <user_id>
      friend pending <user_id>
      friend mutual  <id1> <id2>

    ─── BLOCK ─────────────────────────────────────────
      block   <user_id> <target_id>
      unblock <user_id> <target_id>

    ─── SUGGESTIONS ───────────────────────────────────
      suggest <user_id> [top_k]
      suggest <user_id> --filter age=<min>-<max>
      suggest <user_id> --filter location=<loc>
      suggest <user_id> --filter interests=<i1,i2>
      suggest <user_id> --filter mutual=<min>
      (các filter có thể kết hợp: --filter age=18-25 location=HCM)

    ─── ANALYTICS ─────────────────────────────────────
      analytics path     <id1> <id2>    ← shortest path
      analytics influencer [top_n]
      analytics community
      analytics stats
      analytics similarity <id1> <id2>  ← interest score

    ─── DATA ──────────────────────────────────────────
      data export json <filepath>
      data export csv  <users_path> <edges_path>
      data import json <filepath>
      data import csv  <users_path> <edges_path>
      data generate    [num_users]

    ─── VISUALIZE ─────────────────────────────────────
      viz network  [output_path]
      viz ego      <user_id> [output_path]
      viz path     <id1> <id2>
      viz community

    ─── MISC ──────────────────────────────────────────
      help [command]
      clear
      exit
    """

    def __init__(self, user_manager: UserManager,
                 suggestion_engine: SuggestionEngine,
                 analytics: NetworkAnalytics,
                 data_manager: DataManager,
                 visualizer: Visualizer):
        self._um  = user_manager
        self._se  = suggestion_engine
        self._ana = analytics
        self._dm  = data_manager
        self._viz = visualizer
        self._running = False

    def run(self) -> None:
        """
        Khởi động shell, chạy vòng lặp đọc lệnh cho đến khi gõ 'exit'.
        In banner chào mừng khi bắt đầu.
        """
        pass

    def _parse_command(self, raw: str) -> tuple:
        """
        Parse chuỗi lệnh thành (command_group, subcommand, args, kwargs).
        VD: "suggest U001 --filter age=18-25 location=HCM"
            → ("suggest", None, ["U001"], {"age": (18,25), "location": "HCM"})

        Args:
            raw (str): chuỗi lệnh thô người dùng nhập

        Returns:
            tuple: (group, sub, args, kwargs)
        """
        pass

    def _parse_filter_args(self, kwargs: dict) -> FilterCriteria:
        """
        Chuyển kwargs từ --filter thành FilterCriteria object.

        Args:
            kwargs (dict): VD {"age": "18-25", "location": "HCM"}

        Returns:
            FilterCriteria
        """
        pass

    def _dispatch(self, group: str, sub: str, args: list, kwargs: dict) -> None:
        """
        Điều hướng lệnh đến handler tương ứng.

        Args:
            group  (str) : nhóm lệnh ("user", "friend", "suggest", ...)
            sub    (str) : sub-command ("add", "remove", ...)
            args   (list): positional arguments
            kwargs (dict): keyword arguments (từ --filter, --output, ...)
        """
        pass

    # ── HANDLER METHODS (mỗi nhóm lệnh) ──────────────────────────────

    def _handle_user(self, sub: str, args: list, kwargs: dict) -> None:
        """Xử lý nhóm lệnh 'user ...'"""
        pass

    def _handle_friend(self, sub: str, args: list, kwargs: dict) -> None:
        """Xử lý nhóm lệnh 'friend ...'"""
        pass

    def _handle_suggest(self, args: list, kwargs: dict) -> None:
        """Xử lý lệnh 'suggest ...' kèm filter tùy chọn"""
        pass

    def _handle_analytics(self, sub: str, args: list, kwargs: dict) -> None:
        """Xử lý nhóm lệnh 'analytics ...'"""
        pass

    def _handle_data(self, sub: str, args: list, kwargs: dict) -> None:
        """Xử lý nhóm lệnh 'data ...'"""
        pass

    def _handle_viz(self, sub: str, args: list, kwargs: dict) -> None:
        """Xử lý nhóm lệnh 'viz ...'"""
        pass

    def _print_table(self, headers: list, rows: list) -> None:
        """
        In dữ liệu dạng bảng đẹp ra terminal (không dùng thư viện ngoài).

        Args:
            headers (list[str]): tiêu đề cột
            rows    (list[list]): dữ liệu từng hàng
        """
        pass

    def _print_suggestion(self, result: SuggestionResult) -> None:
        """
        In một gợi ý kèm lý do: "3 bạn chung: An, Bình, Chi | Sở thích: music, travel"
        """
        pass


# ─────────────────────────────────────────────
#  FILE: main.py
# ─────────────────────────────────────────────

def main():
    """
    Entry point: khởi tạo tất cả components và chạy CLI Shell.

    Thứ tự khởi tạo:
        1. UserManager (chứa AVLTree + SocialGraph)
        2. SuggestionEngine(user_manager)
        3. NetworkAnalytics(user_manager)
        4. DataManager(user_manager)
        5. Visualizer(user_manager)
        6. CLIShell(tất cả components trên)
        7. shell.run()
    """
    user_manager      = UserManager()
    suggestion_engine = SuggestionEngine(user_manager)
    analytics         = NetworkAnalytics(user_manager)
    data_manager      = DataManager(user_manager)
    visualizer        = Visualizer(user_manager)

    shell = CLIShell(
        user_manager      = user_manager,
        suggestion_engine = suggestion_engine,
        analytics         = analytics,
        data_manager      = data_manager,
        visualizer        = visualizer,
    )
    shell.run()


if __name__ == "__main__":
    main()