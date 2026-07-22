from user_manager import UserManager
try:
    import pyvis 
    has_pyvis=True
except:
    has_pyvis=False
    print("Chức năng visualizer sẽ không hoạt động, vui lòng tải module pyvis.")

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
        if has_pyvis is False:
            print("Chưa tải module pyvis")
            return
        from pyvis.network import Network

        # highlight_ids mặc định là set rỗng nếu không truyền vào
        highlight_ids = set(highlight_ids) if highlight_ids else set()

        # ── Bảng màu theo location ────────────────────────────────────
        # Mỗi location được gán 1 màu cố định để phân biệt trực quan
        # Nếu location chưa có trong bảng thì dùng màu mặc định
        LOCATION_COLORS = {
            "HCM"     : "#FF6B6B",   # đỏ san hô
            "HN"      : "#4ECDC4",   # xanh ngọc
            "ĐN"      : "#45B7D1",   # xanh dương
            "Cần Thơ" : "#96CEB4",   # xanh lá nhạt
            "Huế"     : "#FFEAA7",   # vàng nhạt
        }
        DEFAULT_COLOR   = "#97C2FC"  # xanh dương nhạt — màu mặc định PyVis
        HIGHLIGHT_COLOR = "#FF0000"  # đỏ tươi — node được highlight

        # ── Khởi tạo PyVis Network ────────────────────────────────────
        # height/width : kích thước khung hiển thị trong HTML
        # bgcolor      : màu nền
        # font_color   : màu chữ nhãn node
        net = Network(
            height     = "750px",
            width      = "100%",
            bgcolor    = "#222222",
            font_color = "white"
        )

        # Bật physics để các node tự sắp xếp đẹp (spring layout)
        net.barnes_hut()

        # ── Thêm tất cả node (user) vào đồ thị ───────────────────────
        all_users = self._um._users
        # print(all_users)

        for user in all_users:
            # Chọn màu: highlight > location > default
            if user.user_id in highlight_ids:
                color = HIGHLIGHT_COLOR
            else:
                color = LOCATION_COLORS.get(user.location, DEFAULT_COLOR)

            # label : chữ hiển thị trên node
            # title : tooltip khi hover chuột vào node
            net.add_node(
                user.user_id,
                label = user.name,
                title = (f"Name: {user.name}\n"
                         f"ID: {user.user_id}\n"
                         f"Tuổi: {user.age}\n"
                         f"Khu vực: {user.location}\n"
                         f"Sở thích: {', '.join(user.interests)}"),
                color = color,
                size  = 100
            )

        # ── Thêm tất cả cạnh (friendship) vào đồ thị ─────────────────
        # get_all_edges() trả về list[tuple(id1, id2)], mỗi cạnh 1 lần
        edges = self._um.get_graph().get_all_edges()
        # print(edges)

        for id1, id2 in edges:
            net.add_edge(id1, id2, color="#AAAAAA")  # xám nhạt cho cạnh

        # ── Xuất ra file HTML ─────────────────────────────────────────
        net.save_graph(output_path)
        
        # Thêm thư viện ở đầu hàm (hoặc đầu file Python của bạn)
        import webbrowser
        import os
        
        # Lấy đường dẫn tuyệt đối của file để trình duyệt có thể đọc được chính xác
        absolute_path = os.path.abspath(output_path)
        
        # Tự động mở file trên trình duyệt mặc định
        webbrowser.open(f"file://{absolute_path}")
        return output_path


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
        if has_pyvis is False:
            print("Chưa tải module pyvis")
            return
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
        if has_pyvis is False:
            print("Chưa tải module pyvis")
            return
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
        if has_pyvis is False:
            print("Chưa tải module pyvis")
            return
        pass
