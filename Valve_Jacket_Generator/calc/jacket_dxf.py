import cadquery as cq


def get_jacket_dxf(*, valve_l=1100, flange_c=2820, valve_c=800, shield_c=2750
                   , gap_left=350, gap_right=310, thck=30, path_sketch='sheet.dxf'
                   , X_offset=50, Y_ofst=400, hole_offset=200):
    valve_d = round(valve_c / 3.14, 3)
    center = valve_l - (2 * thck)  # THE LENGTH OF THE CENTER SIDE (BODY OF VALVE)

    # OFFSETS
    valve_d += hole_offset  # Increasing the hole

    gap_left += X_offset  # (X axis) increasing the left gap
    gap_right += X_offset  # (X axis) increasing the right gap

    flange_c += Y_ofst  # (Y axis) increasing circumference depending on a thickness of jacket (MIDDLE SIDE)
    shield_c += Y_ofst  # (Y axis) increasing circumference depending on a thickness of jacket (TOP SIDES)

    # FOR FINDING THE HOLE COORDINATES
    center_hole = (center - valve_d) / 2

    # VARIABLES FOR ARCS
    # First point of the ThreePointArc is defined by the last drawn line
    arc1_p2 = (valve_d / 2, -(center_hole + (valve_d / 2)))
    arc1_p3 = (0, -(center_hole + valve_d))
    arc2_p2 = ((flange_c - (valve_d / 2)), -(center / 2))
    arc2_p3 = (flange_c, -center_hole)

    # CREATING SKETCH
    jack = (cq.Workplane("XY")
            .moveTo(0.0)  # STARTING POINT
            .lineTo(flange_c, 0.0)  # SECTION 1
            .lineTo(shield_c + (flange_c - shield_c) / 2, gap_left)  # SECTION 1
            .lineTo((flange_c - shield_c) / 2, gap_left)  # SECTION 1
            .lineTo(0.0, 0.0)  # SECTION 1
            .lineTo(0, -center_hole)  # SECTION 2 (part 1)
            .threePointArc(arc1_p2, arc1_p3)  # SECTION 2 (part 1)
            .lineTo(0, -center)  # SECTION 2 (part 1)
            .lineTo(flange_c, -center)  # SECTION 3
            .moveTo(0, -center)  # MOVING THE WORKING POSITION
            .lineTo((flange_c - shield_c) / 2, -(center + gap_right))  # SECTION 3
            .lineTo(shield_c + (flange_c - shield_c) / 2, -(center + gap_right))  # SECTION 3
            .lineTo(flange_c, -center)  # SECTION 3
            .lineTo(flange_c, -(center_hole + valve_d))  # SECTION 2 (part 2)
            .threePointArc(arc2_p2, arc2_p3)  # SECTION 2 (part 2)
            .lineTo(flange_c, 0)  # SECTION 2 (part 2)
            .close()
            )

    return cq.exporters.exportDXF(jack, path_sketch)