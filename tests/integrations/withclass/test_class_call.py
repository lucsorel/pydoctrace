from math import pi

from pydoctrace.doctrace import trace_to_puml

from tests.modules.withclass import Circle


@trace_to_puml
def call_circle_area():
    circle = Circle(0, 0, 2)
    circle_area = circle.area()
    area_formula = circle.area_formula()  # static method called from an instance
    extruded_volume_formula = circle.extruded_volume_formula()  # class method called on the instance
    return circle_area, area_formula, extruded_volume_formula


def test_call_circle_area():
    circle_area, area_formula, extruded_volume_formula = call_circle_area()
    assert abs(circle_area - 4 * pi) < 0.001
    assert extruded_volume_formula == 'h.PI.r²'
