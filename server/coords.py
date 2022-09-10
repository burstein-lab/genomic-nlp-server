class Point:
    """Defines a point coordinations and its value in space
    """

    def __init__(self, id_, x_coord, y_coord, value) -> None:
        self.id_ = id_
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.value = value

    @classmethod
    def fromdict(cls, id_, x_coord, y_coord, value):
        return cls(id_, x_coord, y_coord, value)

    def todict(self) -> dict:
        return {
            "id": self.id_,
            "x": self.x_coord,
            "y": self.y_coord,
            "value": self.value,
        }
