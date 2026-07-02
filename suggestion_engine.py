import heapq
from models       import SuggestionResult, FilterCriteria
from models       import User
from user_manager import UserManager

class SuggestionEngine:
    """
    Lõi thuật toán gợi ý kết bạn.

    Chiến lược scoring (weighted):
        score = mutual_count * W_MUTUAL + common_interests * W_INTEREST
        W_MUTUAL   = 1.0  (trọng số bạn chung)
        W_INTEREST = 0.5  (trọng số sở thích chung)
    """

    W_MUTUAL   = 1.0
    W_INTEREST = 0.5

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    def _compute_score(self, user: User, candidate: User,
                       mutual_count: int) -> float:
        """
        Tính điểm tổng hợp cho một gợi ý.

        Args:
            user         (User): người đang được gợi ý cho
            candidate    (User): người được gợi ý
            mutual_count (int) : số bạn chung đã tính

        Returns:
            float: điểm tổng hợp
        """
        pass

    def _apply_filters(self, user: User, candidates: list,
                       filters: FilterCriteria) -> list:
        """
        Áp dụng FilterCriteria lên danh sách SuggestionResult.
        Lọc theo: age_range, location, interests, min_mutual.

        Args:
            user       (User)            : người dùng hiện tại
            candidates (list[SuggestionResult]): danh sách thô
            filters    (FilterCriteria)  : tiêu chí lọc

        Returns:
            list[SuggestionResult]: danh sách đã lọc
        """
        pass

    def suggest(self, user_id: str, top_k: int = 10,
                filters: FilterCriteria = None) -> list:
        """
        Gợi ý bạn bè cho user_id.

        Thuật toán:
            1. Dùng SocialGraph.get_candidates_at_depth2() → dict{id: mutual_count}
            2. Loại bỏ user bị block (từ cả 2 chiều)
            3. Tính score tổng hợp cho mỗi candidate
            4. Dùng Max-Heap (heapq) lấy top_k — O(n log k)
            5. Áp dụng filters nếu có
            6. Đính kèm mutual_names và common_interests vào kết quả

        Args:
            user_id  (str)                  : ID người cần gợi ý
            top_k    (int)                  : số gợi ý tối đa trả về
            filters  (FilterCriteria | None): bộ lọc tùy chọn

        Returns:
            list[SuggestionResult]: sắp xếp giảm dần theo score
        """
        pass

    def suggest_by_interest_only(self, user_id: str, top_k: int = 10) -> list:
        """
        Gợi ý dựa thuần túy trên sở thích chung (không cần bạn chung).
        Dùng khi user mới, chưa có bạn bè nào.

        Args:
            user_id (str)
            top_k   (int)

        Returns:
            list[SuggestionResult]: sắp xếp theo số sở thích chung giảm dần
        """
        pass
