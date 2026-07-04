# ─────────────────────────────────────────────
#  FILE: network_analytics.py
# ─────────────────────────────────────────────

import heapq

from models       import User
from user_manager import UserManager


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
        # BFS thực sự nằm trong SocialGraph, ở đây chỉ gọi lại và làm giàu dữ liệu
        path = self._graph.shortest_path(from_id, to_id)

        if not path:
            return {"path": [], "path_names": [], "degree": -1}

        path_names = []
        for uid in path:
            user = self._um.get_user(uid)
            path_names.append(user.name if user else uid)

        return {
            "path"      : path,
            "path_names": path_names,
            "degree"    : len(path) - 1,
        }

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
        if top_n <= 0:
            return []

        all_users = self._um.get_all_users()
        if not all_users:
            return []

        # Heap key: (-degree, name) → khi heapify/pop sẽ ưu tiên degree cao nhất,
        # và nếu bằng degree thì tên A→Z được lấy trước (tie-break ổn định).
        heap = []
        for user in all_users:
            degree = self._graph.degree(user.user_id)
            heapq.heappush(heap, (-degree, user.name, user.user_id, user))

        result = []
        n = min(top_n, len(heap))
        for _ in range(n):
            neg_degree, _name, _uid, user = heapq.heappop(heap)
            result.append({
                "user"        : user,
                "friend_count": -neg_degree,
            })

        return result

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
        components = self._graph.find_connected_components()

        raw = []
        for component in components:
            members = []
            for uid in component:
                user = self._um.get_user(uid)
                if user is not None:
                    members.append(user)
            # Sắp xếp thành viên theo tên cho dễ đọc / ổn định
            members.sort(key=lambda u: u.name)
            raw.append(members)

        # Sắp xếp các community giảm dần theo kích thước
        raw.sort(key=len, reverse=True)

        result = []
        for idx, members in enumerate(raw, start=1):
            result.append({
                "community_id": idx,
                "size"        : len(members),
                "members"     : members,
            })

        return result

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
        all_users = self._um.get_all_users()
        total_users = len(all_users)

        total_friendships = len(self._graph.get_all_edges())

        avg_friends = (2 * total_friendships / total_users) if total_users > 0 else 0.0

        if total_users > 1:
            density = (2 * total_friendships) / (total_users * (total_users - 1))
        else:
            density = 0.0

        communities = self.detect_communities()
        num_communities = len(communities)
        largest_community = communities[0]["size"] if communities else 0

        isolated_users = sum(
            1 for user in all_users if self._graph.degree(user.user_id) == 0
        )

        return {
            "total_users"      : total_users,
            "total_friendships": total_friendships,
            "avg_friends"      : avg_friends,
            "density"          : density,
            "num_communities"  : num_communities,
            "largest_community": largest_community,
            "isolated_users"   : isolated_users,
        }

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
        user1 = self._um.get_user(user_id1)
        user2 = self._um.get_user(user_id2)

        if user1 is None or user2 is None:
            return {
                "common"    : [],
                "score"     : 0.0,
                "user1_only": [],
                "user2_only": [],
            }

        set1 = set(user1.interests)
        set2 = set(user2.interests)

        common = set1 & set2
        union  = set1 | set2

        score = (len(common) / len(union)) if union else 0.0

        return {
            "common"    : sorted(common),
            "score"     : score,
            "user1_only": sorted(set1 - set2),
            "user2_only": sorted(set2 - set1),
        }