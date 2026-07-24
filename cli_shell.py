from models            import FilterCriteria, SuggestionResult
from user_manager      import UserManager
from suggestion_engine import SuggestionEngine
from network_analytics import NetworkAnalytics
from data_manager      import DataManager
from visualizer        import Visualizer
import traceback


class CLIShell:
    """
    Interactive Command-Line Shell.
    Thay vì menu số, dùng lệnh text giống terminal thực:

    COMMANDS (nhóm theo chức năng):
    ─── USER MANAGEMENT ───────────────────────────────
      user add <Nguyen_Van_A> <age> <Da_Nang> <da_bong,cau_long,...>
      user remove <id>
      user update <id> <field1>=<value1> <field2>=<value2> ...
      user get <id>
      user list
      user search <Van_A>          ← fuzzy search theo tên
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
      data export json <filepath=data.json>
      data export csv  <users_path> <edges_path>
      data import json <filepath>
      data import csv  <users_path> <edges_path>
      data generate    [num_users] [avg_friends=N]

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
        self._running=True
        try:
            self._dm.import_json("data.json")
        except:
            pass
        while self._running:
            command=input("InputCommand> ")
            try:
                command_parsed=self._parse_command(command)
                if not command_parsed:
                    continue
                self._dispatch(command_parsed)
            except Exception as e:
                print("Đã xảy ra lỗi:", e)
                # traceback.print_exc()

                print('Nhập "help" để xem lệnh\n\n')
            self._dm.export_json("data.json")
        pass

    def _parse_command(self, raw: str) -> list:
        "chia token cho command, không hạ chữ thường để giữ nguyên tên/location"
        return raw.strip().split()

    # def _parse_filter_args(self, kwargs: dict) -> FilterCriteria:
    #     """
    #     Chuyển kwargs từ --filter thành FilterCriteria object.

    #     Args:
    #         kwargs (dict): VD {"age": "18-25", "location": "HCM"}

    #     Returns:
    #         FilterCriteria
    #     """
    #     pass

    def _dispatch(self, command_parsed) -> None:
        """
        Điều hướng lệnh đến handler tương ứng.
        """
        handler_method=command_parsed[0].lower()
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
        else:
            raise Exception(f'Không có nhóm lệnh {handler_method}')


    # ── HANDLER METHODS (mỗi nhóm lệnh) ──────────────────────────────

    def _handle_user(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'user ...'"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu subcommand")
        else:
            sub_command = command_parsed[1].lower()
        if sub_command == "add":
            if len(command_parsed) != 6:
                raise Exception('''Sai cú pháp. Cú pháp đúng: "user add <Nguyen_Van_A> <age> <Da_Nang> <da_bong,cau_long,...>" 
                                Lỗi thường gặp: mỗi mục phải là một từ duy nhất, sử dụng gạch dưới thay cho dấu cách, giữa các sở thích không có dấu cách''')
            name=command_parsed[2].replace("_", " ")
            age=int(command_parsed[3])
            location=command_parsed[4]
            interest=command_parsed[5].split(",")
            self._um.add_user(name,age,location,interest)
        elif sub_command == "graph_list" :
            self._print_graph_components(self._um.get_graph().find_connected_components())
        elif sub_command == "remove" :
            if len(command_parsed) != 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "user remove <id>" ')
            id=command_parsed[2]
            self._um.remove_user(id)
        elif sub_command == "update":
            if len(command_parsed) < 4:
                raise Exception('''Sai cú pháp. Cú pháp đúng: "user update <id> <field1>=<value1> <field2>=<value2> ..." 
                                Lỗi thường gặp: mỗi mục phải là một từ duy nhất, sử dụng gạch dưới thay cho dấu cách, giữa các sở thích không được có dấu cách, hai bên dấu bằng không được có dấu cách. ''')
            id = command_parsed[2].upper()
            updates = {}
            for pair in command_parsed[3:]:
                if "=" not in pair:
                    raise Exception(f'''Sai cú pháp ở "{pair}". Mỗi trường phải có dạng field=value''')
                field, value = pair.split("=", 1)
                field = field.lower()
                if field == "age":
                    value = int(value)
                elif field == "name":
                    value = value.replace("_", " ")
                elif field == "interests":
                    value = value.split(",")
                updates[field] = value
            ok = self._um.update_user(id, **updates)
            print("Cập nhật thành công" if ok else "Không tìm thấy user")
        elif sub_command == "get":
            if len(command_parsed) != 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "user get <id>" ')
            id = command_parsed[2].upper()
            print(self._format_user(self._um.get_user(id)))
        elif sub_command == "list":
            if len(command_parsed) != 2:
                raise Exception('Sai cú pháp. Cú pháp đúng: "user list" ')
            print(self._format_user_list(self._um.list_users_sorted()))
        elif sub_command == "search":
            if len(command_parsed) != 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "user search <nguyen_van_a>  ← fuzzy search theo tên" ')
            print(self._format_user_list(self._um.search_by_name_fuzzy(command_parsed[2].replace("_", " "))))
        elif sub_command == "search-age":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "user search-age <min> <max>  ← tìm theo khoảng tuổi" ')
            min_age = int(command_parsed[2])
            max_age = int(command_parsed[3])
            print(self._format_user_list(self._um.search_by_age_range(min_age, max_age)))
        else:
            raise Exception(f'Nhóm lệnh {command_parsed[0]} không có subcommand {command_parsed[1]}')
            


    def _handle_friend(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'friend ...'"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu subcommand")
        else:
            sub_command = command_parsed[1].lower()
        if sub_command == "request":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend request <from_id> <to_id>" ')
            from_id=command_parsed[2].upper()
            to_id=command_parsed[3].upper()
            status = self._um.send_friend_request(from_id,to_id)
            messages = {
                "sent"            : f"Đã gửi lời mời kết bạn từ {from_id} đến {to_id}.",
                "already_friends" : f"{from_id} và {to_id} đã là bạn bè.",
                "blocked"         : "Không thể gửi lời mời vì một trong hai người đã chặn người kia.",
                "already_pending" : "Lời mời kết bạn đã được gửi trước đó, đang chờ phản hồi.",
            }
            print(messages.get(status, status))
        elif sub_command == "cancel":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend cancel <from_id> <to_id>" ')
            from_id=command_parsed[2].upper()
            to_id=command_parsed[3].upper()
            print("Đã hủy lời mời kết bạn." if self._um.cancel_friend_request(from_id,to_id) else "Không tìm thấy lời mời nào.")
        elif sub_command == "accept":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend accept <user_id> <from_id>" ')
            user_id=command_parsed[2].upper()
            from_id=command_parsed[3].upper()
            print("Đã chấp nhận lời mời kết bạn." if self._um.accept_friend_request(user_id,from_id) else "Không tìm thấy lời mời nào.")
        elif sub_command == "decline":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend decline <user_id> <from_id>" ')
            user_id=command_parsed[2].upper()
            from_id=command_parsed[3].upper()
            print("Đã từ chối lời mời kết bạn." if self._um.decline_friend_request(user_id,from_id) else "Không tìm thấy lời mời nào.")
        elif sub_command == "remove" :
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend remove <id1> <id2>" ')
            id1=command_parsed[2].upper()
            id2=command_parsed[3].upper()
            print("Đã hủy kết bạn." if self._um.unfriend(id1,id2) else "Hai người này chưa phải bạn bè.")
        elif sub_command == "list" :
            if len(command_parsed) != 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend list <user_id>" ')
            user_id=command_parsed[2].upper()
            self._print_id_list(self._um.get_graph().get_friends(user_id), f"Bạn bè của {user_id}")
        elif sub_command == "pending" :
            if len(command_parsed) != 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend pending <user_id>" ')
            user_id=command_parsed[2].upper()
            self._print_pending_requests(self._um.get_pending_requests(user_id), user_id)
        elif sub_command == "mutual" :
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "friend mutual <id1> <id2>" ')
            id1=command_parsed[2].upper()
            id2=command_parsed[3].upper()
            self._print_id_list(self._um.get_mutual_friends(id1,id2), f"Bạn chung giữa {id1} và {id2}")

        else:
            raise Exception(f'Nhóm lệnh {command_parsed[0]} không có subcommand {command_parsed[1]}')


    def _handle_suggest(self, command_parsed: list) -> None:
        """Xử lý lệnh 'suggest ...' kèm filter tùy chọn"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu user_id")
        else:
            user_id = command_parsed[1].upper()
            sub_command = command_parsed[2:]
        
        # defaut
        top_k=10
        age_range=None
        location=None
        interest=None
        min_mutual=1

        for e in sub_command:
            if "top_" in e:
                top_k = int(e.replace("top_", ""))
            elif "--filter" in e:
                pass
            elif "age" in e:
                age_range=tuple(int(e2) for e2 in e.replace("age=", "").split("-"))
            elif "location" in e:
                location=e.replace("location=", "")
            elif "interest" in e:
                interest=tuple(e.replace("interests=", "").split(","))
            elif "mutual" in e:
                min_mutual=int(e.replace("mutual=", ""))
            else:
                raise Exception(f'''Filter {e} không hợp lệ.
                                Lỗi thường gặp: mỗi mục phải là một từ duy nhất, sử dụng gạch dưới thay cho dấu cách, giữa các sở thích không có dấu cách''')

        

        results = self._se.suggest(user_id,top_k,FilterCriteria(age_range,location,interest,min_mutual))
        if not results:
            print("Không có gợi ý nào.")
        for r in results:
            self._print_suggestion(r)

    def _handle_analytics(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'analytics ...'"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu subcommand")
        else:
            sub_command = command_parsed[1].lower()
        if sub_command == "path":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "analytics path <id1> <id2>" ')
            id1=command_parsed[2].upper()
            id2=command_parsed[3].upper()
            self._print_path(self._ana.shortest_path(id1,id2), id1, id2)
        elif sub_command == "influencer":
            if len(command_parsed) not in [2,3]:
                raise Exception('Sai cú pháp. Cú pháp đúng: "analytics influencer [top_n]" ')
            top_n = int(command_parsed[2]) if len(command_parsed)==3 else 5
            self._print_influencers(self._ana.top_influencers(top_n))
        elif sub_command == "community":
            if len(command_parsed) != 2:
                raise Exception('Sai cú pháp. Cú pháp đúng: "analytics community" ')
            self._print_communities(self._ana.detect_communities())
        elif sub_command == "stats":
            if len(command_parsed) != 2:
                raise Exception('Sai cú pháp. Cú pháp đúng: "analytics stats" ')
            self._print_network_stats(self._ana.network_stats())
        elif sub_command == "similarity":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "analytics similarity <id1> <id2>" ')
            id1=command_parsed[2].upper()
            id2=command_parsed[3].upper()
            self._print_similarity(self._ana.common_interest_score(id1,id2), id1, id2)
        else:
            raise Exception(f'Nhóm lệnh {command_parsed[0]} không có subcommand {command_parsed[1]}')

    def _handle_data(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'data ...'"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu subcommand")
        else:
            sub_command = command_parsed[1].lower()
        if sub_command == "generate":
            if len(command_parsed) < 2:
                raise Exception('''Sai cú pháp. Cú pháp đúng: "data generate [num_users] [avg_friends=N]"
                                VD: data generate 60 avg_friends=3''')
            num_users = 50
            avg_friends = 5
            rest = command_parsed[2:]
            if rest and "=" not in rest[0]:
                num_users = int(rest[0])
                rest = rest[1:]
            for pair in rest:
                if "=" not in pair:
                    raise Exception(f'Sai cú pháp ở "{pair}". Mỗi tham số phải có dạng field=value')
                field, value = pair.split("=", 1)
                field = field.lower()
                if field == "avg_friends":
                    avg_friends = int(value)
                else:
                    raise Exception(f'Tham số "{field}" không hợp lệ. Dùng avg_friends')
            self._print_generate_result(self._dm.generate_sample_data(num_users, avg_friends))
        elif sub_command == "export":
            if len(command_parsed) < 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "data export json <filepath=data.json>" hoặc "data export csv <users_path> <edges_path>" ')
            export_type=command_parsed[2].lower()
            if export_type == "json":
                if len(command_parsed) == 3:
                    print("Exported" if self._dm.export_json("data.json") else "Failed to export")
                elif len(command_parsed) != 4:
                    raise Exception('Sai cú pháp. Cú pháp đúng: "data export json <filepath=data.json>" ')
                else:
                    print("Exported" if self._dm.export_json(command_parsed[3]) else "Failed to export")
            elif export_type == "csv":
                if len(command_parsed) != 5:
                    raise Exception('Sai cú pháp. Cú pháp đúng: "data export csv <users_path> <edges_path>" ')
                ok = self._dm.export_csv(command_parsed[3], command_parsed[4])
                print("Exported" if ok else "Failed to export")
            else:
                raise Exception(f'data export không hỗ trợ định dạng "{export_type}"')
        elif sub_command == "import":
            if len(command_parsed) < 3:
                raise Exception('Sai cú pháp. Cú pháp đúng: "data import json <filepath>" hoặc "data import csv <users_path> <edges_path>" ')
            import_type=command_parsed[2].lower()
            if import_type == "json":
                if len(command_parsed) != 4:
                    raise Exception('Sai cú pháp. Cú pháp đúng: "data import json <filepath>" ')
                self._print_import_result(self._dm.import_json(command_parsed[3]), "Nhập JSON")
            elif import_type == "csv":
                if len(command_parsed) != 5:
                    raise Exception('Sai cú pháp. Cú pháp đúng: "data import csv <users_path> <edges_path>" ')
                self._print_import_result(self._dm.import_csv(command_parsed[3], command_parsed[4]), "Nhập CSV")
            else:
                raise Exception(f'data import không hỗ trợ định dạng "{import_type}"')
        else:
            raise Exception(f'Nhóm lệnh {command_parsed[0]} không có subcommand {command_parsed[1]}')

    def _handle_viz(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'viz ...'"""
        if len(command_parsed) == 1:
            raise Exception("Thiếu subcommand")
        else:
            sub_command = command_parsed[1].lower()
        if sub_command == "network":
            if len(command_parsed) not in [2,3]:
                raise Exception('Sai cú pháp. Cú pháp đúng: "viz network [output_path]" ')

            if len(command_parsed) == 3:
                output=command_parsed[2]
                self._print_viz_result(self._viz.render_full_network(output))
            else:
                self._print_viz_result(self._viz.render_full_network())

        elif sub_command == "ego":
            if len(command_parsed) not in [3,4]:
                raise Exception('Sai cú pháp. Cú pháp đúng: "viz ego <user_id> [output_path]" ')
            user_id=command_parsed[2].upper()
            if len(command_parsed) == 4:
                self._print_viz_result(self._viz.render_ego_network(user_id, command_parsed[3]))
            else:
                self._print_viz_result(self._viz.render_ego_network(user_id))

        elif sub_command == "path":
            if len(command_parsed) != 4:
                raise Exception('Sai cú pháp. Cú pháp đúng: "viz path <id1> <id2>" ')
            id1=command_parsed[2].upper()
            id2=command_parsed[3].upper()
            result = self._ana.shortest_path(id1, id2)
            if not result["path"]:
                print(f"Không có đường đi giữa {id1} và {id2} để vẽ.")
            else:
                self._print_viz_result(self._viz.render_path(result["path"]))

        elif sub_command == "community":
            if len(command_parsed) != 2:
                raise Exception('Sai cú pháp. Cú pháp đúng: "viz community" ')
            communities = self._ana.detect_communities()
            self._print_viz_result(self._viz.render_communities(communities))

        else:
            raise Exception(f'Nhóm lệnh {command_parsed[0]} không có subcommand {command_parsed[1]}')



    def _handle_block(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh 'block ...'"""
        if len(command_parsed) != 3:
            raise Exception('Sai cú pháp. Cú pháp đúng: "block <user_id> <target_id>" hoặc "unblock <user_id> <target_id>" ')
        action    = command_parsed[0].lower()
        user_id   = command_parsed[1].upper()
        target_id = command_parsed[2].upper()
        if action == "block":
            ok = self._um.block_user(user_id, target_id)
            print(f"Đã chặn {target_id}." if ok else f"{target_id} đã bị chặn từ trước.")
        else:
            ok = self._um.unblock_user(user_id, target_id)
            print(f"Đã bỏ chặn {target_id}." if ok else f"{target_id} chưa từng bị chặn.")

    def _handle_misc(self, command_parsed: list) -> None:
        """Xử lý nhóm lệnh khác"""
        sub_command = command_parsed[0]
        
        if sub_command == "help":
            if len(command_parsed)>2:
                raise Exception('Sai cú pháp. Cú pháp đúng: "help [command]" ')
            if len(command_parsed)==2:
                help_category=command_parsed[1]
            else:
                help_category=input("Vui lòng chọn loại chức năng(user/friend/block/suggestion/analytics/data/visualize/misc/all): ")
            if help_category == "user":
                print("""
─── USER MANAGEMENT ───────────────────────────────
    user add <Nguyen_Van_A> <age> <Da_Nang> <da_bong,cau_long,...>
    user remove <id>
    user update <id> <field1>=<value1> <field2>=<value2> ...
    user get <id>
    user list
    user search <Van_A>          ← fuzzy search theo tên
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
    (các filter có thể kết hợp: [top_k] --filter age=18-25 location=HCM)
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
    data export json <filepath=data.json>
    data export csv  <users_path> <edges_path>
    data import json <filepath>
    data import csv  <users_path> <edges_path>
    data generate    [num_users] [avg_friends=N]     
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
                print("""─── MISC ──────────────────────────────────────────
    help [command]
    clear
    exit           
""")
            elif help_category == "all":
                print("""
    COMMANDS (nhóm theo chức năng):
─── USER MANAGEMENT ───────────────────────────────
    user add <Nguyen_Van_A> <age> <Da_Nang> <da_bong,cau_long,...>
    user remove <id>
    user update <id> <field1>=<value1> <field2>=<value2> ...
    user get <id>
    user list
    user search <nguyen_van_a>          ← fuzzy search theo tên
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
    data export json <filepath=data.json>
    data export csv  <users_path> <edges_path>
    data import json <filepath>
    data import csv  <users_path> <edges_path>
    data generate    [num_users] [avg_friends=N]

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
            else:
                print(f'Không có mục trợ giúp "{help_category}". '
                      'Dùng: user/friend/block/suggestion/analytics/data/visualize/misc/all')
        elif sub_command == "clear":
            import os
            os.system("cls" if os.name == "nt" else "clear")
        elif sub_command == "exit":
            self._running=False
        


    def _print_table(self, headers: list, rows: list) -> None:
        """
        In dữ liệu dạng bảng đẹp ra terminal (không dùng thư viện ngoài).

        Args:
            headers (list[str]): tiêu đề cột
            rows    (list[list]): dữ liệu từng hàng
        """
        if not headers:
            return
        str_rows = [[str(cell) for cell in row] for row in rows]
        col_widths = [len(h) for h in headers]
        for row in str_rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        def format_row(row):
            return " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))

        header_line = format_row(headers)
        separator   = "-+-".join("-" * w for w in col_widths)
        print(header_line)
        print(separator)
        for row in str_rows:
            print(format_row(row))

    def _print_path(self, result: dict, id1: str, id2: str) -> None:
        """In kết quả 'analytics path' dạng chuỗi liên kết dễ đọc."""
        if not result["path"]:
            print(f"Không tìm thấy đường kết nối giữa {id1} và {id2}.")
            return
        chain = " → ".join(
            f"{uid}({name})" for uid, name in zip(result["path"], result["path_names"])
        )
        print(f"Đường đi ngắn nhất ({result['degree']} bậc ngăn cách):")
        print(f"  {chain}")

    def _print_influencers(self, results: list) -> None:
        """In danh sách 'analytics influencer' dạng bảng."""
        if not results:
            print("Không có dữ liệu người dùng.")
            return
        rows = [
            [i + 1, r["user"].user_id, r["user"].name, r["friend_count"]]
            for i, r in enumerate(results)
        ]
        self._print_table(["#", "ID", "Tên", "Số bạn"], rows)

    def _print_communities(self, communities: list) -> None:
        """In danh sách 'analytics community' dạng bảng."""
        if not communities:
            print("Không có cộng đồng nào.")
            return
        rows = []
        for c in communities:
            members_str = ", ".join(f"{m.name}({m.user_id})" for m in c["members"])
            rows.append([c["community_id"], c["size"], members_str])
        self._print_table(["Cộng đồng", "Kích thước", "Thành viên"], rows)

    def _print_network_stats(self, stats: dict) -> None:
        """In 'analytics stats' dạng bảng, làm tròn số thập phân cho dễ đọc."""
        labels = {
            "total_users"      : "Tổng số user",
            "total_friendships": "Tổng số kết bạn",
            "avg_friends"      : "Bạn bè trung bình",
            "density"          : "Mật độ mạng lưới",
            "num_communities"  : "Số cộng đồng",
            "largest_community": "Cộng đồng lớn nhất",
            "isolated_users"   : "User không có bạn",
        }
        rows = []
        for key, label in labels.items():
            value = stats.get(key)
            if isinstance(value, float):
                value = round(value, 4)
            rows.append([label, value])
        self._print_table(["Chỉ số", "Giá trị"], rows)

    def _print_similarity(self, result: dict, id1: str, id2: str) -> None:
        """In 'analytics similarity' dễ đọc."""
        common     = ", ".join(result["common"])     if result["common"]     else "không có"
        only1      = ", ".join(result["user1_only"])  if result["user1_only"]  else "không có"
        only2      = ", ".join(result["user2_only"])  if result["user2_only"]  else "không có"
        print(f"Độ tương đồng (Jaccard) giữa {id1} và {id2}: {result['score']:.2f}")
        print(f"  Sở thích chung : {common}")
        print(f"  Chỉ {id1} có   : {only1}")
        print(f"  Chỉ {id2} có   : {only2}")

    def _format_id_set(self, ids) -> str:
        """Chuyển 1 tập/list user_id thô thành chuỗi 'Tên(ID), Tên(ID)' dễ đọc,
        thay vì in ra set() thô kiểu {'U001', 'U002'}."""
        if not ids:
            return "không có"
        parts = []
        for uid in sorted(ids):
            user = self._um.get_user(uid)
            parts.append(f"{user.name}({uid})" if user else uid)
        return ", ".join(parts)

    def _print_id_list(self, ids, title: str) -> None:
        print(f"{title}: {self._format_id_set(ids)}")

    def _print_pending_requests(self, requests: list, user_id: str) -> None:
        """In danh sách lời mời kết bạn đang chờ dạng bảng, thay vì list[FriendRequest] thô."""
        if not requests:
            print(f"{user_id} không có lời mời kết bạn nào đang chờ.")
            return
        rows = []
        for req in requests:
            from_user = self._um.get_user(req.from_id)
            from_name = from_user.name if from_user else req.from_id
            rows.append([req.from_id, from_name, req.status.value])
        self._print_table(["Từ ID", "Tên", "Trạng thái"], rows)

    def _print_graph_components(self, components: list) -> None:
        """In danh sách connected components (lệnh 'user graph_list') dạng bảng dễ đọc."""
        if not components:
            print("Không có dữ liệu.")
            return
        rows = []
        for i, comp in enumerate(components, start=1):
            names = self._format_id_set(comp)
            rows.append([i, len(comp), names])
        self._print_table(["Nhóm", "Kích thước", "Thành viên"], rows)

    def _print_import_result(self, result: dict, label: str = "Nhập dữ liệu") -> None:
        print(f"{label} thành công: {result['users_loaded']} user, "
              f"{result['friendships_loaded']} lượt kết bạn.")

    def _print_generate_result(self, result: dict) -> None:
        print(f"Đã tạo {result['users_created']} user, "
              f"{result['friendships_created']} lượt kết bạn "
              f"(mất {result['execution_time_ms']} ms).")

    def _print_viz_result(self, output_path) -> None:
        """In kết quả lệnh viz. Các hàm render_* trả về None khi thiếu pyvis
        (và tự in cảnh báo bên trong rồi) -> ở đây không được print(None) đè lên."""
        if output_path:
            print(f"Đã tạo file: {output_path}")

    def _print_suggestion(self, result: SuggestionResult) -> None:
        """
        In một gợi ý kèm lý do: "3 bạn chung: An, Bình, Chi | Sở thích: music, travel"
        """
        mutual_str   = ", ".join(result.mutual_names) if result.mutual_names else "không có"
        interest_str = ", ".join(result.common_interests) if result.common_interests else "không có"
        print(f"- {result.user.name} ({result.user.user_id}) | "
              f"{result.mutual_count} bạn chung: {mutual_str} | "
              f"Sở thích chung: {interest_str} | Điểm: {result.score:.2f}")
    
    def _format_user(self,user) -> str:
        """Hiển thị 1 user dạng bảng đẹp."""
        if user is None:
            return "Không tìm thấy user."
        interests_str = ", ".join(user.interests) if user.interests else "(không có)"
        return (
            f"┌─ User: {user.user_id}\n"
            f"│  Tên      : {user.name}\n"
            f"│  Tuổi     : {user.age}\n"
            f"│  Địa chỉ  : {user.location}\n"
            f"│  Sở thích : {interests_str}\n"
            f"└─────────────────────"
        )


    def _format_user_list(self,users: list) -> str:
        """Hiển thị danh sách user dạng bảng ngắn gọn."""
        if not users:
            return "Không có user nào."
        header = f"{'ID':<8}{'Tên':<20}{'Tuổi':<6}{'Địa chỉ':<15}{'Sở thích'}"
        lines = [header, "-" * len(header)]
        for u in users:
            interests_str = ", ".join(u.interests) if u.interests else "-"
            lines.append(f"{u.user_id:<8}{u.name:<20}{u.age:<6}{u.location:<15}{interests_str}")
        return "\n".join(lines)