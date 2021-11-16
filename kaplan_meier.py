from PyQt5.QtCore import QPointF


class KaplanMeierAnalyzer:
    def analyze(self, keys: list, data: list) -> list:
        sorted_data = self._sort_data(keys, data)
        uncensored_data = self._get_uncensored_data(keys, sorted_data)
        points = self._calculate_points_for_chart(keys, uncensored_data)
        return self._generate_chart_data(points)

    def _sort_data(self, keys: list, data: list) -> list:
        return sorted(data, key=lambda row: row[keys[-2]])

    def _get_uncensored_data(self, keys: list, data: list) -> list:
        uncensored_data = []
        for row in data:
            if row[keys[1]] == "F":
                uncensored_data.append(row)
        return uncensored_data

    def _calculate_points_for_chart(self, keys: list, data: list) -> list:
        points = []
        num, surv_val, num_of_records = 0, 1, len(data)
        while num < num_of_records:
            failed_units = 1
            while (
                num + failed_units < num_of_records
                and data[num][keys[-2]] == data[num + failed_units][keys[-2]]
            ):
                failed_units += 1
            surv_val = surv_val * (1 - failed_units / data[num][keys[-1]])
            points.append((data[num][keys[-2]], surv_val))
            num += failed_units
        return points

    def _generate_chart_data(self, data: list) -> list:
        return [QPointF(x, y) for x, y in data]
