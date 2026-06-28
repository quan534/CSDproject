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