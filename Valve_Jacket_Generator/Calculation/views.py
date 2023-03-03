import cadquery as cq
from math import pi
from django.shortcuts import render
from django.http import HttpResponse

def flanges(*, flange_c, pipe_c, gap_left, gap_right, shield_c, thck=5, left_side=False, bolts_num=8, bolts_d=5):
    """
    GENERATES TWO FLANGES WITH PIPE AND SHIELD
    WORKS BOTH FOR LEFT AND RIGHT SIDE
    """
    # try:
    # GET DIAMETER
    flange_d = flange_c / pi
    pipe_d = pipe_c / pi
    shield_d = shield_c / pi

    # ERROR CATCHING
    if pipe_d >= flange_d:
        raise ValueError('"pipe_c" cannot be greater than or equal to "flange_c"')
    elif (flange_d - pipe_d) <= bolts_d:
        raise ValueError('Holes do not fit this flange. Make holes smaller ("bolts_d") or increase "flange_d"')

    # BASE CYLINDER
    base = cq.Workplane("XZ").cylinder(thck, flange_d)

    # CENTER HOLE
    front_face = cq.Workplane("XZ").workplane(offset=thck).moveTo(0, 0)
    sketch = front_face.circle(pipe_d).extrude(-thck * 2)
    result = base.cut(sketch)

    # SMALL HOLES
    ofst = pipe_d + ((flange_d - pipe_d) / 2)
    for i in range(bolts_num):
        angle = i * (360 / bolts_num)
        x = ofst * cos(radians(angle))
        y = ofst * sin(radians(angle))
        front_face = cq.Workplane("XZ").workplane(offset=thck).moveTo(x, y)
        sketch = front_face.circle(bolts_d).extrude(-thck * 2)
        result = result.cut(sketch)

    # MIRRORING THE FLANGES
    result = result.translate(result.val().BoundingBox().center.multiply(-1))
    mirXZ_neg = result.mirror(mirrorPlane="XZ", basePointVector=(0, (thck / 2) + 0.1, 0))
    result = result.union(mirXZ_neg, breakpoint)

    # PIPE WITH THE SHIELD
    face, coef, gap = "<Y", 1, gap_right
    if left_side:
        face, coef, gap = ">Y", -1, gap_left

    result = (result
              .faces(face)
              .circle(pipe_d)
              .extrude(gap / coef)
              .faces(face)
              .circle(shield_d)
              .extrude(700 / coef)
              )

    return result


def body(*, valve_l=1100, flange_c=2820, pipe_c=1950, valve_c=800, thck=20, act_h=50, actuator_gap=200):
    # Get diameter
    flange_d = flange_c / pi
    pipe_d = pipe_c / pi
    valve_d = valve_c / pi

    if valve_d >= valve_l:
        raise ValueError('"valve_c" cannot be greater than or equal to "valve_l"')

    # Get length of body excluding the flange thickness
    total = valve_l - (thck * 4)  # flange is always 50mm

    side = (total - valve_d) / 2

    # creating the body of valve
    bdy = (cq.Workplane("XZ")
           .move(0, 0)
           .circle(pipe_d)
           .workplane(offset=-side)
           .circle(flange_d)
           .loft(combine=True)
           .faces(">Y")
           .circle(flange_d)
           .extrude(-valve_d)
           .faces(">Y")
           .circle(flange_d)
           .workplane(offset=side)
           .circle(pipe_d)
           .loft(combine=True)
           )

    # adding the actuator to the top of body
    actuator = (cq.Workplane("XY")
                .move(0, (total / 2))
                .circle(valve_d / 2)
                .extrude(flange_d + (flange_d / 2))
                )

    bdy = bdy.union(actuator)

    return bdy


def build(right_flange, left_flange, bdy, path_step='valve.step'):
    valve = (cq.Assembly()
             .add(right_flange
                  , loc=cq.Location((0, 0, 0), (0, 1, 0), 0)
                  , name="right"
                  , color=cq.Color("lightgray")
                  )
             .add(left_flange
                  , name="left"
                  , color=cq.Color("lightgray")
                  )
             .add(bdy
                  , name="body"
                  , color=cq.Color("lightgray")
                  )
             )

    (valve
     .constrain("right@faces@>Y", "body@faces@<Y", "Plane")
     .constrain("body@faces@>Y", "left@faces@<Y", "Plane")
     )

    valve.solve()

    valve.save(path_step)


def get_jacket_dxf(*, valve_l=1100, flange_c=2820, valve_c=800, shield_c=2750
                   , gap_left=350, gap_right=310, thck=30, path_sketch='sheet.dxf'
                   , X_offset=50, Y_ofst=400, hole_offset=200):
    valve_d = round(valve_c / pi, 3)
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

    cq.exporters.exportDXF(jack, path_sketch)


def get_valve_stp(*, flange_c, pipe_c, shield_c, valve_l, valve_c, gap_left, gap_right, actuator_gap, thck, bolts_num=8,
                  bolts_d=5, actuator_type='electric', path_step='valve.step'):
    r_flange = flanges(flange_c=flange_c
                       , pipe_c=pipe_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , shield_c=shield_c
                       , left_side=False
                       , thck=thck
                       , bolts_num=bolts_num
                       , bolts_d=bolts_d
                       )

    l_flange = flanges(flange_c=flange_c
                       , pipe_c=pipe_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , shield_c=shield_c
                       , left_side=True
                       , thck=thck
                       , bolts_num=bolts_num
                       , bolts_d=bolts_d
                       )

    bdy = body(valve_l=valve_l
               , flange_c=flange_c
               , pipe_c=pipe_c
               , valve_c=valve_c
               , thck=thck
               )

    build(r_flange, l_flange, bdy, path_step)


def generate_files(request):
    if request.method == 'POST':
        flange_c = request.POST.get('flange_c')
        flange_thck = request.POST.get('flange_thck')
        shield_c = request.POST.get('shield_c')
        pipe_c = request.POST.get('pipe_c')
        valve_c = request.POST.get('valve_c')
        valve_l = request.POST.get('valve_l')
        gap_left = request.POST.get('gap_left')
        gap_right = request.POST.get('gap_right')

        # Generate the files using the form data
        get_valve_stp(flange_c=flange_c
                      , valve_l=valve_l
                      , shield_c=shield_c
                      , pipe_c=pipe_c
                      , valve_c=valve_c
                      , gap_left=gap_left
                      , gap_right=gap_right
                      , thck=flange_thck
                      , path_step='temp\\valve_3D.step'
                      )
        return HttpResponse('Files generated successfully!')
    else:
        return render(request, 'generate_files.html')