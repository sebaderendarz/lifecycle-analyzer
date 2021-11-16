import math
from typing import Tuple

from PyQt5.QtCore import QPointF


class WeibullAnalyzer:
    def analyze(self, keys: list, data: list) -> Tuple[list, str, str]:
        sorted_and_ranked_data = self._sort_and_rank_data(keys, data)
        uncensored_data = self._get_uncensored_data(keys, sorted_and_ranked_data)
        survival_points = self._calculate_estimate_survival_values(keys, uncensored_data)
        k, lamb = self._calculate_weibull_parameters(survival_points)
        chart_data = self._generate_chart_data(keys, uncensored_data, k, lamb)
        return chart_data, f"{k:.8f}", f"{lamb:.8f}"

    def _sort_and_rank_data(self, keys: list, data: list) -> list:
        data_sorted_by_ttl = sorted(data, key=lambda row: row[keys[-1]])
        data_len = len(data_sorted_by_ttl)
        keys.append("Rank")
        for x in range(1, data_len + 1):
            data_sorted_by_ttl[data_len - x][keys[-1]] = x
        return data_sorted_by_ttl

    def _get_uncensored_data(self, keys: list, data: list) -> list:
        uncensored_data = []
        for row in data:
            if row[keys[1]] == "F":
                uncensored_data.append(row)
        return uncensored_data

    def _calculate_estimate_survival_values(self, keys: list, data: list) -> list:
        points = []
        prev_value = 1
        for row in data:
            y = prev_value * row[keys[-1]] / (row[keys[-1]] + 1)
            prev_value = y
            y = math.log(-math.log(y))
            x = math.log(row[keys[-2]])
            points.append((x, y))
        return points

    def _calculate_weibull_parameters(self, data: list) -> Tuple[float, float]:
        N = len(data)
        sum_x, sum_y, sum_x2, sum_xy = 0, 0, 0, 0
        for row in data:
            sum_x += row[0]
            sum_y += row[1]
            sum_x2 += row[0] ** 2
            sum_xy += row[0] * row[1]
        a = (N * sum_xy - sum_x * sum_y) / (N * sum_x2 - sum_x ** 2)
        b = (sum_y - a * sum_x) / N
        return a, math.exp((-b) / a)

    def _generate_chart_data(self, keys: list, data: list, k: float, lamb: float) -> list:
        return [QPointF(row[keys[-2]], math.exp(-((row[keys[-2]] / lamb) ** k))) for row in data]
