from models       import User, FriendRequest, RequestStatus
from avl_tree     import AVLTree
from social_graph import SocialGraph
from typing import Optional
from datetime import datetime
from collections import defaultdict

class UserManager:
    """
        _pending  (dict[str, list[FriendRequest]]): pending[to_id] = [requests]
        _blocked  (dict[str, set[str]])     : blocked[user_id] = set bị chặn
    """

    def __init__(self):
        self._users:   list     = []
        self._id_map:  dict     = {}
        self._avl_name = AVLTree()
        self._graph    = SocialGraph()
        self._pending: dict     = defaultdict(set)
        self._blocked: dict     = defaultdict(set)
        self._next_id: int      = 1       # auto-increment ID


    def _generate_id(self) -> str:
        """Sinh user_id mới dạng 'U001', 'U002', ..."""
        gen_id=f"U{self._next_id:03}"
        self._next_id+=1
        return gen_id
    
    def _add_block(self,user_id,target_id) -> None:
        user_block_list=self._blocked[user_id]
        if target_id in user_block_list:
            return False
        else:
            user_block_list.add(target_id)
            return True
        


    # ── CRUD ──────────────────────────────────────────────────────────

    def add_user(self, name: str, age: int, location: str,
                 interests: list) -> User:
        user_id=self._generate_id()
        user=User(user_id,name,age,location,interests)
        self._graph.add_node(user.user_id)
        self._avl_name.insert(user)
        self._id_map[user_id]=user
        self._users.append(user)
        return user

    def remove_user(self, user_id: str) -> bool:
        try:
            self._graph.remove_node(user_id)
            self._avl_name.delete(self.get_user(user_id).name)
            return True
        except Exception as e:
            return False


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
        return self._id_map[user_id]

    def get_all_users(self) -> list:
        return self._users

    # ── SEARCH ────────────────────────────────────────────────────────

    def search_by_name_exact(self, name: str) -> Optional[User]:
        return self._avl_name.search_exact(name)
        

    def search_by_name_fuzzy(self, query: str) -> list:
        return [user for user in self._users if query in user.name]
        

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
        return self._avl_name.inorder()

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
        is_friend=self._graph.are_friends(from_id,to_id)
        is_blocked=self.is_blocked(from_id,to_id)
        is_sent=bool([e for e in self.get_pending_requests(to_id) if e.from_id==from_id])
        if is_blocked: return "blocked"
        if is_sent: return "already_pending"
        if is_friend: return "already_friends"
        self._pending[to_id].add(FriendRequest(from_id,to_id,RequestStatus.PENDING,datetime.now()))
        return "sent"


    def cancel_friend_request(self, from_id: str, to_id: str) -> bool:
        """
        Hủy lời mời kết bạn đã gửi (unrequest).

        Args:
            from_id (str)
            to_id   (str)

        Returns:
            bool: True nếu hủy thành công
        """
        for e in self.get_pending_requests(to_id):
            if e.from_id == from_id and e.to_id == to_id:
                self._pending.remove(e)
                return True
        return False


    def accept_friend_request(self, user_id: str, from_id: str) -> bool:
        """
        Chấp nhận lời mời → tạo cạnh 2 chiều trong SocialGraph.

        Args:
            user_id (str): người nhận (đang accept)
            from_id (str): người đã gửi request

        Returns:
            bool: True nếu thành công
        """

        is_exist=self.cancel_friend_request(from_id,user_id)
        if is_exist:
            self._graph.add_edge(user_id,from_id)
            return True
        return False

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
        is_exist=self.cancel_friend_request(from_id,user_id)
        if is_exist:
            self._graph.add_edge(user_id,from_id)
            self._add_block(user_id,from_id)
            return True
        return False
        

    def unfriend(self, user_id1: str, user_id2: str) -> bool:
        """
        Hủy kết bạn — xóa cạnh trong SocialGraph.

        Args:
            user_id1 (str)
            user_id2 (str)

        Returns:
            bool: True nếu thành công
        """
        if self._graph.are_friends(user_id1,user_id2):
            self._graph.remove_edge(user_id1,user_id2)
            return True
        else:
            return False

    

    def get_pending_requests(self, user_id: str) -> list:
        """
        Lấy danh sách lời mời kết bạn đang chờ của user.

        Args:
            user_id (str)

        Returns:
            list[FriendRequest]: các request có status = PENDING
        """

        return self._pending[user_id]

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
        if self.is_blocked(user_id,target_id):
            return False
        else:
            self.decline_friend_request(user_id,target_id)
            self.unfriend(user_id,target_id)
            return True
        


    def unblock_user(self, user_id: str, target_id: str) -> bool:
        """
        Bỏ chặn người dùng.

        Args:
            user_id   (str)
            target_id (str)

        Returns:
            bool
        """
        if self.is_blocked(user_id,target_id):
            self._blocked[user_id].remove(target_id)
            return True
        else:
            return False
        

    def is_blocked(self, user_id: str, target_id: str) -> bool:
        """
        Kiểm tra user_id có block target_id không (hoặc ngược lại).

        Args:
            user_id   (str)
            target_id (str)

        Returns:
            bool: True nếu một trong hai đã block nhau
        """
        return user_id in self._blocked[target_id]
    

    def get_graph(self) -> SocialGraph:
        """Trả về SocialGraph để các module khác dùng."""
        return self._graph
    
    # khác
    def get_mutual_friends(self,id1,id2):
        return self._graph.get_mutual_friends()

