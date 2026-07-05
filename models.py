from typing import Optional
from enum import Enum


class RequestStatus(Enum):
    PENDING  = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class User:
    """
    Đại diện một người dùng trong mạng xã hội.

    Attributes:
        user_id   (str)       : ID duy nhất, dạng "U001"
        name      (str)       : Họ và tên đầy đủ
        age       (int)       : Tuổi (dùng để filter gợi ý)
        location  (str)       : Khu vực / thành phố
        interests (list[str]) : Danh sách sở thích, VD ["music", "travel"]
    """

    def __init__(self, user_id: str, name: str, age: int,
                 location: str, interests: list = None):
        self.user_id   = user_id
        self.name      = name
        self.age       = age
        self.location  = location
        self.interests = interests if interests is not None else []

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, {self.age}, {self.location})"

    def to_dict(self) -> dict:
        # return một dict với keys, values tương ứng là tên các attributes và giá trị của nó của của đối tượng user
        return {"user_id": self.user_id, "name": self.name, "age": self.age, "location": self.location, "interests": self.interests}

        pass

    @staticmethod
    def from_dict(data: dict) -> "User":
        # Tạo User từ dict (dùng khi import file).
        return User(data["user_id"],data["name"],data["age"],data["location"],data["interests"])
        pass

    def __str__(self):
        return f"User({self.user_id}, {self.name}, {self.age}, {self.location})"


class FriendRequest:
    """
    Đại diện một lời mời kết bạn.

    Attributes:
        from_id   (str)          : ID người gửi
        to_id     (str)          : ID người nhận
        status    (RequestStatus): PENDING / ACCEPTED / DECLINED
        timestamp (float)        : Unix timestamp lúc gửi
    """

    def __init__(self, from_id: str, to_id: str,
                 status: RequestStatus = RequestStatus.PENDING,
                 timestamp: float = 0.0):
        self.from_id   = from_id
        self.to_id     = to_id
        self.status    = status
        self.timestamp = timestamp

    def __repr__(self):
        return f"FriendRequest({self.from_id} → {self.to_id}, {self.status.value})"

    def __str__(self):
        return f"FriendRequest({self.from_id} → {self.to_id}, {self.status.value})"



class SuggestionResult:
    """
    Kết quả một gợi ý kết bạn (dùng để hiển thị cho người dùng).

    Attributes:
        user          (User)      : Người được gợi ý
        mutual_count  (int)       : Số bạn chung
        mutual_names  (list[str]) : Tên các bạn chung (để hiển thị lý do)
        common_interests (list[str]): Sở thích chung
        score         (float)     : Điểm tổng hợp (mutual + interest bonus)
    """

    def __init__(self, user: User, mutual_count: int,
                 mutual_names: list = None,
                 common_interests: list = None,
                 score: float = 0.0):
        self.user             = user
        self.mutual_count     = mutual_count
        self.mutual_names     = mutual_names     if mutual_names     is not None else []
        self.common_interests = common_interests if common_interests is not None else []
        self.score            = score

    def __repr__(self):
        return f"SuggestionResult({self.user.name}, mutual={self.mutual_count}, score={self.score})"

    def __str__(self):
        return f"SuggestionResult({self.user.name}, mutual={self.mutual_count}, score={self.score})"


class FilterCriteria:
    """
    Bộ lọc cho danh sách gợi ý. None = bỏ qua tiêu chí đó.

    Attributes:
        age_range      (tuple|None) : (min_age, max_age), VD (18, 25)
        location       (str|None)   : Lọc theo khu vực chính xác
        interests      (list|None)  : Lọc user có ÍT NHẤT 1 sở thích chung
        min_mutual     (int)        : Số bạn chung tối thiểu (mặc định 0)
    """

    def __init__(self, age_range: Optional[tuple] = None,
                 location: Optional[str] = None,
                 interests: Optional[list] = None,
                 min_mutual: int = 0):
        self.age_range  = age_range
        self.location   = location
        self.interests  = interests
        self.min_mutual = min_mutual

    def __repr__(self):
        return (f"FilterCriteria(age={self.age_range}, location={self.location}, "
                f"interests={self.interests}, min_mutual={self.min_mutual})")

