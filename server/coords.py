class Point:
    """Defines a point coordinations and its value in space
    """

    def __init__(self, x_coord, y_coord, value) -> None:
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.value = value

    @classmethod
    def fromdict(cls, x, y, value):
        return cls(x, y, value)

    def todict(self) -> dict:
        return {
            "x": self.x_coord,
            "y": self.y_coord,
            "name": self.value,
        }
