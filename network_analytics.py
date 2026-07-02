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

