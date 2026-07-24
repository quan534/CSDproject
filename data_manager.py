import json
import csv
import random
import time
from datetime import datetime
from collections import defaultdict
from social_graph import SocialGraph 
from avl_tree import AVLTree
from models       import User
from user_manager import UserManager
class DataManager:
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
    def import_json(self, filepath: str) ->dict:
        try:
            with open(filepath,"r",encoding="utf-8") as f:
                data=json.load(f)
            users_loaded=0
            friendships_loaded=0
            self._um._users.clear()
            self._um._id_map.clear()
            self._um._graph = SocialGraph()
            self._um._avl_name = AVLTree()
            self._um._pending = defaultdict(set)
            self._um._blocked = defaultdict(set)
            
            max_id=0
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
            self._um._next_id=max_id+1
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
    def import_csv(self,
                   users_filepath: str,
                   edges_filepath: str) -> dict:
        try:
            users_loaded = 0
            friendships_loaded = 0
            self._um._users.clear()
            self._um._id_map.clear()
            self._um._graph = SocialGraph()
            self._um._avl_name = AVLTree()
            self._um._pending = defaultdict(set)
            self._um._blocked = defaultdict(set)
            max_id = 0
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
    def generate_sample_data(self,
                             num_users: int = 50,
                             avg_friends: int = 5,
                             seed: int = 42) -> dict:
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
    def clear_data(self):
        self._um._users.clear()
        self._um._id_map.clear()
        self._um._graph = SocialGraph()
        self._um._avl_name = AVLTree()
        self._um._pending = defaultdict(set)
        self._um._blocked = defaultdict(set)
        self._um._next_id = 1
    def statistics(self):
        graph = self._um.get_graph()
        return {
            "total_users": len(self._um.get_all_users()),
            "total_friendships": len(graph.get_all_edges())
        }