from models            import FilterCriteria, SuggestionResult
from user_manager      import UserManager
from suggestion_engine import SuggestionEngine
from network_analytics import NetworkAnalytics
from data_manager      import DataManager
from visualizer        import Visualizer


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
        print("Chào mừng đến với hệ thống Quản lí người dùng")
        print('Nhập "help" để xem lệnh')
        print("============================")
        while True:
            command=input("InputCommand> ").lower()
            if command == "exit" : break
            try:
                command_parsed=self._parse_command(command)
                self._dispatch(command_parsed)
            except Exception as e:
                print("Đã xảy ra lỗi:", e)
                print('Cú pháp không hợp lệ, nhập "help" để xem lệnh\n\n')
        pass

    def _parse_command(self, raw: str) -> tuple:
        "chia token cho command"
        return raw.strip().split()

    def _parse_filter_args(self, kwargs: dict) -> FilterCriteria:
        """
        Chuyển kwargs từ --filter thành FilterCriteria object.

        Args:
            kwargs (dict): VD {"age": "18-25", "location": "HCM"}

        Returns:
            FilterCriteria
        """
        pass

    def _dispatch(self, command_parsed) -> None:
        """
        Điều hướng lệnh đến handler tương ứng.
        """
        handler_method=command_parsed[0]
        if handler_method == "user":
            self._handle_user(command_parsed)
        elif handler_method == "suggest":
            self._handle_suggest(command_parsed)
        elif handler_method == "analytics":
            self._handle_analytics(command_parsed)
        elif handler_method == "data":
            self._handle_data(command_parsed)
        elif handler_method == "viz":
            self._handle_viz(command_parsed)
        elif handler_method == "friend":
            self._handle_friend(command_parsed)
        elif handler_method in ["block","unblock"]:
            self._handle_block(command_parsed)
        elif handler_method in ["help","clear","exit"]:
            self._handle_misc(command_parsed)


    # ── HANDLER METHODS (mỗi nhóm lệnh) ──────────────────────────────

    def _handle_user(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'user ...'"""
        sub_command = command_parsed[1]
        if sub_command == "add":
            name=command_parsed[1]
            age=int(command_parsed[2])
            location=command_parsed[3]
            interest=command_parsed[4].split(",")
            self._um.add_user(name,age,location,interest)
        elif sub_command == "graph_list" :
            print(self._um.get_graph().find_connected_components())
        pass

    def _handle_friend(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'friend ...'"""
        pass

    def _handle_suggest(self, command_parsed: list) -> None:
        """Xử lý lệnh 'suggest ...' kèm filter tùy chọn"""
        pass

    def _handle_analytics(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'analytics ...'"""
        pass

    def _handle_data(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'data ...'"""
        pass

    def _handle_viz(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'viz ...'"""
        pass

    def _handle_block(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'block ...'"""
        pass

    def _handle_misc(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh khác"""
        sub_command = command_parsed[0]
        
        if sub_command == "help":
            if len(command_parsed)>1:
                help_category=command_parsed[1]
            else:
                help_category=input("Vui lòng chọn loại chức năng(user/friend/block/suggestion/analytics/data/visualize/misc/all): ")
            if help_category == "user":
                print("""
    ─── USER MANAGEMENT ───────────────────────────────
      user add <name> <age> <location> <interest1,interest2,...>
      user remove <id>
      user update <id> <field> <value>
      user get <id>
      user list
      user search <query>          ← fuzzy search theo tên
      user search-age <min> <max>  ← tìm theo khoảng tuổi

""")
            elif help_category == "friend":
                print("""
    ─── FRIEND MANAGEMENT ─────────────────────────────
      friend request <from_id> <to_id>
      friend cancel  <from_id> <to_id>
      friend accept  <user_id> <from_id>
      friend decline <user_id> <from_id>
      friend remove  <id1> <id2>
      friend list    <user_id>
      friend pending <user_id>
      friend mutual  <id1> <id2>

""")
            elif help_category == "block":
                print("""
    ─── BLOCK ─────────────────────────────────────────
      block   <user_id> <target_id>
      unblock <user_id> <target_id>

""")
            elif help_category == "suggestion":
                print("""
    ─── SUGGESTIONS ───────────────────────────────────
      suggest <user_id> [top_k]
      suggest <user_id> --filter age=<min>-<max>
      suggest <user_id> --filter location=<loc>
      suggest <user_id> --filter interests=<i1,i2>
      suggest <user_id> --filter mutual=<min>
      (các filter có thể kết hợp: --filter age=18-25 location=HCM)

""")
            elif help_category == "analytics":
                print("""
    ─── ANALYTICS ─────────────────────────────────────
      analytics path     <id1> <id2>    ← shortest path
      analytics influencer [top_n]
      analytics community
      analytics stats
      analytics similarity <id1> <id2>  ← interest score

""")
            elif help_category == "data":
                print("""
    ─── DATA ──────────────────────────────────────────
      data export json <filepath>
      data export csv  <users_path> <edges_path>
      data import json <filepath>
      data import csv  <users_path> <edges_path>
      data generate    [num_users]
                      
""")
            elif help_category == "visualize":
                print("""
    ─── VISUALIZE ─────────────────────────────────────
      viz network  [output_path]
      viz ego      <user_id> [output_path]
      viz path     <id1> <id2>
      viz community

""")
            elif help_category == "misc":
                print("""
    ─── MISC ──────────────────────────────────────────
      help [command]
      clear
      exit
                      
""")
            elif help_category == "all":
                print("""
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
""")
                    
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
