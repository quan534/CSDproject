from user_manager import UserManager

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
