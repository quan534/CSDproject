Đây là phiên bản đã bỏ hết docstring và comment (`#`), chỉ giữ code:

```python
import heapq
from models       import SuggestionResult, FilterCriteria
from models       import User
from user_manager import UserManager


class SuggestionEngine:
    W_MUTUAL   = 1.0
    W_INTEREST = 0.5

    def __init__(self, user_manager: UserManager):
        self._um = user_manager

    def _compute_score(self, user: User, candidate: User,
                       mutual_count: int) -> float:
        common_interests = set(user.interests) & set(candidate.interests)
        return (mutual_count * self.W_MUTUAL
                + len(common_interests) * self.W_INTEREST)

    def _apply_filters(self, user: User, candidates: list,
                       filters: FilterCriteria) -> list:
        if filters is None:
            return candidates

        filtered = []
        for result in candidates:
            candidate = result.user

            if result.mutual_count < filters.min_mutual:
                continue

            if filters.age_range is not None:
                min_age, max_age = filters.age_range
                if not (min_age <= candidate.age <= max_age):
                    continue

            if filters.location is not None:
                if candidate.location != filters.location:
                    continue

            if filters.interests is not None:
                if not (set(candidate.interests) & set(filters.interests)):
                    continue

            filtered.append(result)

        return filtered

    def suggest(self, user_id: str, top_k: int = 10,
                filters: FilterCriteria = None) -> list:
        user = self._um.get_user(user_id)
        if user is None:
            return []

        graph = self._um.get_graph()
        raw_candidates = graph.get_candidates_at_depth2(user_id)

        results = []
        for candidate_id, mutual_count in raw_candidates.items():
            if self._um.is_blocked(user_id, candidate_id):
                continue

            candidate = self._um.get_user(candidate_id)
            if candidate is None:
                continue

            score = self._compute_score(user, candidate, mutual_count)

            mutual_ids = graph.get_mutual_friends(user_id, candidate_id)
            mutual_names = []
            for mid in mutual_ids:
                mutual_user = self._um.get_user(mid)
                if mutual_user is not None:
                    mutual_names.append(mutual_user.name)

            common_interests = list(set(user.interests) & set(candidate.interests))

            results.append(SuggestionResult(
                user=candidate,
                mutual_count=mutual_count,
                mutual_names=mutual_names,
                common_interests=common_interests,
                score=score
            ))

        results = self._apply_filters(user, results, filters)
        top_results = heapq.nlargest(top_k, results, key=lambda r: r.score)

        return top_results

    def suggest_by_interest_only(self, user_id: str, top_k: int = 10) -> list:
        user = self._um.get_user(user_id)
        if user is None:
            return []

        graph = self._um.get_graph()
        direct_friends = graph.get_friends(user_id)

        results = []
        for candidate in self._um.get_all_users():
            candidate_id = candidate.user_id

            if candidate_id == user_id:
                continue
            if candidate_id in direct_friends:
                continue
            if self._um.is_blocked(user_id, candidate_id):
                continue

            common_interests = list(set(user.interests) & set(candidate.interests))
            if not common_interests:
                continue

            score = len(common_interests) * self.W_INTEREST

            results.append(SuggestionResult(
                user=candidate,
                mutual_count=0,
                mutual_names=[],
                common_interests=common_interests,
                score=score
            ))

        top_results = heapq.nlargest(top_k, results, key=lambda r: r.score)
        return top_results