from math import pi


class Circle:
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius

    def area(self):
        return pi * (self.radius**2)

    @classmethod
    def extruded_volume_formula(cls):
        return f'h.{cls.area_formula()}'

    @staticmethod
    def area_formula():
        return 'PI.r²'
