import os
from pathlib import Path

import build123d as b123d

big_od = 150
hole_sep = 125
hole_d = 8 + 1
hole_count = 8

raise_dist = (
    9  # Height of middle bolt sticking out
    + 3  # Amount the outsides are bent downwards
)

bolt_head_d = 20  # Allow a socket on.

bolt_length = 16

# M8 specs
nut_flats_width = 13 + 0.2
nut_height = 8

plate_t = 2

counterbore_depth = (
    raise_dist  # Total thickness of the adapter
    - (
        bolt_length
        - nut_height  # Want it to go though the nut all the way
        - 4  # Assume the main base has about 4mm of material between this adapter and the nut.
    )
)

# Border around the edge to the gape in the middle.
border_w = 25


def make_adapter():
    # Orientation: build in the 3d-print orientation. Solid plate on the bottom.
    with b123d.BuildPart() as adapter:
        b123d.Cylinder(radius=big_od / 2, height=raise_dist)

        # Holes around perimeter
        with b123d.Locations(adapter.faces().sort_by(b123d.Axis.Z)[-1]):
            with b123d.PolarLocations(radius=hole_sep / 2, count=hole_count):
                b123d.CounterBoreHole(
                    radius=hole_d / 2,
                    counter_bore_radius=bolt_head_d / 2,
                    counter_bore_depth=counterbore_depth,
                )

        # Hole in the middle for space saving (makes the plate)
        with b123d.Locations(adapter.faces().sort_by(b123d.Axis.Z)[0]):
            b123d.Hole(radius=(big_od - border_w * 2) / 2, depth=raise_dist - plate_t)

        # Nuts, inserted from the bottom.
        with b123d.Locations(adapter.faces().sort_by(b123d.Axis.Z)[0]):
            polar_locations = b123d.PolarLocations(
                radius=hole_sep / 2,
                count=hole_count,
                start_angle=360 / hole_count / 2,
            )
            with polar_locations:
                b123d.Hole(radius=hole_d / 2)

        with b123d.BuildSketch(
            adapter.faces().sort_by(b123d.Axis.Z)[0], mode=b123d.Mode.SUBTRACT
        ):
            with polar_locations:
                b123d.RegularPolygon(
                    radius=nut_flats_width / 2,
                    side_count=6,
                    # For nuts, must set the width as the inscribed (minor) radius
                    major_radius=False,
                )
        b123d.extrude(amount=-nut_height, mode=b123d.Mode.SUBTRACT)

    return adapter


if __name__ == "__main__":
    adapter = make_adapter()

    if not os.getenv("CI"):
        from ocp_vscode import show

        print("Showing CAD model(s)")
        show(adapter)

    (export_folder := Path(__file__).parent.with_name("build")).mkdir(exist_ok=True)
    adapter.part.export_stl(str(export_folder / "adapter.stl"))
    adapter.part.export_step(str(export_folder / "adapter.step"))
