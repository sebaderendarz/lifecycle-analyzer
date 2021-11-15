from typing import Tuple


class WeibullAnalyzer:
    def analyze(self, keys: list, data: list) -> Tuple[list, float, float]:
        sorted_and_ranked_data = self._sort_and_rank_data(keys, data)
        uncensored_data = self._get_uncensored_data(keys, sorted_and_ranked_data)
        print(uncensored_data)

        return [], 0.1, 0.2

    def _sort_and_rank_data(self, keys: list, data: list) -> list:
        data_sorted_by_ttl = sorted(data, key=lambda row: row[keys[-1]])
        data_len = len(data_sorted_by_ttl)
        for x in range(1, data_len + 1):
            data_sorted_by_ttl[data_len - x]["Rank"] = x
        return data_sorted_by_ttl

    def _get_uncensored_data(self, keys: list, data: list) -> list:
        uncensored_data = []
        for row in data:
            if row[keys[1]] == "F":
                uncensored_data.append(row)
        return uncensored_data
