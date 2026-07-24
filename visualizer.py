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
            "HCM"       : "#FF6B6B",   # đỏ san hô
            "HN"        : "#4ECDC4",   # xanh ngọc
            "Đà Nẵng"   : "#45B7D1",   # xanh dương (khớp với DataManager.SAMPLE_LOCATIONS)
            "Cần Thơ"   : "#96CEB4",   # xanh lá nhạt
            "Huế"       : "#FFEAA7",   # vàng nhạt
            "Hải Phòng" : "#DDA0DD",   # tím nhạt
            "Bình Dương": "#FFA07A",   # cam nhạt
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
        self._open_in_browser(output_path)
        return output_path

    def _open_in_browser(self, output_path: str) -> None:
        """Mở file HTML vừa tạo bằng trình duyệt mặc định."""
        import webbrowser
        import os
        absolute_path = os.path.abspath(output_path)
        webbrowser.open(f"file://{absolute_path}")

    def _node_title(self, user) -> str:
        """Tooltip dùng chung khi hover vào node."""
        return (f"Name: {user.name}\n"
                f"ID: {user.user_id}\n"
                f"Tuổi: {user.age}\n"
                f"Khu vực: {user.location}\n"
                f"Sở thích: {', '.join(user.interests)}")

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
        center_user = self._um.get_user(user_id)
        if center_user is None:
            print(f"Không tìm thấy user {user_id}")
            return

        from pyvis.network import Network

        graph = self._um.get_graph()
        direct_friends = graph.get_friends(user_id)

        # Bạn của bạn (depth 2), loại trừ chính user và các bạn trực tiếp
        depth2 = set()
        for fid in direct_friends:
            depth2 |= graph.get_friends(fid)
        depth2.discard(user_id)
        depth2 -= direct_friends

        node_ids = {user_id} | direct_friends | depth2

        CENTER_COLOR = "#FF0000"  # trung tâm — đỏ
        FRIEND_COLOR = "#4ECDC4"  # bạn trực tiếp — xanh ngọc
        FOF_COLOR    = "#97C2FC"  # bạn của bạn — xanh nhạt

        net = Network(height="750px", width="100%",
                      bgcolor="#222222", font_color="white")
        net.barnes_hut()

        for uid in node_ids:
            user = self._um.get_user(uid)
            if user is None:
                continue
            if uid == user_id:
                color, size = CENTER_COLOR, 40
            elif uid in direct_friends:
                color, size = FRIEND_COLOR, 25
            else:
                color, size = FOF_COLOR, 15
            net.add_node(uid, label=user.name, title=self._node_title(user),
                         color=color, size=size)

        for id1, id2 in graph.get_all_edges():
            if id1 in node_ids and id2 in node_ids:
                net.add_edge(id1, id2, color="#AAAAAA")

        net.save_graph(output_path)
        self._open_in_browser(output_path)
        return output_path

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
        if not path_ids:
            print("Không có đường đi để hiển thị.")
            return

        from pyvis.network import Network

        path_set = set(path_ids)
        path_edges = {
            frozenset((path_ids[i], path_ids[i + 1]))
            for i in range(len(path_ids) - 1)
        }

        PATH_COLOR    = "#FF0000"
        DEFAULT_COLOR = "#97C2FC"

        net = Network(height="750px", width="100%",
                      bgcolor="#222222", font_color="white")
        net.barnes_hut()

        for user in self._um.get_all_users():
            if user.user_id in path_set:
                color, size = PATH_COLOR, 35
            else:
                color, size = DEFAULT_COLOR, 15
            net.add_node(user.user_id, label=user.name, title=self._node_title(user),
                         color=color, size=size)

        for id1, id2 in self._um.get_graph().get_all_edges():
            if frozenset((id1, id2)) in path_edges:
                net.add_edge(id1, id2, color=PATH_COLOR, width=4)
            else:
                net.add_edge(id1, id2, color="#555555")

        net.save_graph(output_path)
        self._open_in_browser(output_path)
        return output_path

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
        if not communities:
            print("Không có cộng đồng nào để hiển thị.")
            return

        from pyvis.network import Network

        PALETTE = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE",
        ]

        net = Network(height="750px", width="100%",
                      bgcolor="#222222", font_color="white")
        net.barnes_hut()

        for community in communities:
            color = PALETTE[(community["community_id"] - 1) % len(PALETTE)]
            for user in community["members"]:
                title = (self._node_title(user) +
                          f"\nCộng đồng: #{community['community_id']}")
                net.add_node(user.user_id, label=user.name, title=title,
                             color=color, size=20)

        for id1, id2 in self._um.get_graph().get_all_edges():
            net.add_edge(id1, id2, color="#AAAAAA")

        net.save_graph(output_path)
        self._open_in_browser(output_path)
        return output_path