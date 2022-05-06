from typing import List


class Point:
    def __init__(self, x, y, value) -> None:
        self.x = x
        self.y = y
        self.value = value

    def todict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "name": self.value,
        }


class Coords:
    def __init__(self, points: List[Point]) -> None:
        self.points = points

    def get_rect_points_by_distance(self, center_x, center_y, x_distance, y_distance):
        result = []
        for i in self.points:
            x_ok = center_x - x_distance < i.x < center_x + x_distance
            y_ok = center_y - y_distance < i.y < center_y + y_distance
            if x_ok and y_ok:
                result.append(i)

        return result
