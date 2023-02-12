# pip install --pre git+https://github.com/CadQuery/cadquery.git

# Jacket thickness - 30mm

import math
import cadquery as cq

def flanges(*, flange_c, pipe_c, gap_left, gap_right, shield_c, thck=5, left_side=False, bolts_num=8, bolts_d=5):
    '''
    GENERATES TWO FLANGES WITH PIPE AND SHIELD
    WORKS BOTH FOR LEFT AND RIGHT SIDE
    '''
    # try:
    # GET DIAMETER
    flange_d = flange_c / math.pi
    pipe_d = pipe_c / math.pi
    shield_d = shield_c / math.pi

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
        x = ofst * math.cos(math.radians(angle))
        y = ofst * math.sin(math.radians(angle))
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


def body(*, valve_l=1100, flange_c=2820, pipe_c=1950, valve_c=800, thck=20):
    # Get diameter
    flange_d = flange_c / math.pi
    pipe_d = pipe_c / math.pi
    valve_d = valve_c / math.pi

    if valve_d >= valve_l:
        raise ValueError('"valve_c" cannot be greater than or equal to "valve_l"')

    # Get length of body excluding the flange thickness
    total = valve_l - (thck * 4)  # flange is always 50mm

    side = (total - valve_d) / 2

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

    return bdy


def build(right_flange, left_flange, bdy, path='valve.step'):
    valve = (cq.Assembly()
             .add(right_flange
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

    user = input("Generated without errors. Save this valve as STEP?(y\\n) ")
    if user == 'y':
        valve.save(path)
        print(f"Saved to directory: {path}")
    print('\nProgram finished')


def get_jacket_dxf(*, valve_l=1100, flange_c=2820, valve_c=800, shield_c=2750
                   , gap_left=350, gap_right=310, shield_ofst=10, hole_ofst=10
                   , thck=30):
    valve_d = valve_c / pi
    center = valve_l - (2 * thck)
    center_hole = (center - valve_d) / 2
    print(center_hole)

    p1 = (0, -392.611)
    p2 = (127.389, -520.00)
    p3 = (0, -647.389)

    # Create the arc by passing the three points to the arc() method
    arc = cq.Edge.makeThreePointArc(p1, p2, p3).close()

    start_point = (0.0, 0.0)
    jack = (cq.Workplane("XY")
            .moveTo(0.0)
            .line(flange_c, 0.0)  # SECTION 1
            .lineTo(shield_c + (flange_c - shield_c) / 2, gap_left)  # SECTION 1
            .lineTo((flange_c - shield_c) / 2, gap_left)  # SECTION 1
            .lineTo(0.0, 0.0)  # SECTION 1
            .lineTo(0, -center)  # SECTION 2
            .lineTo(flange_c, -center)  # SECTION 2
            .lineTo(flange_c, 0)  # SECTION 2
            .moveTo(0, -center)  # SECTION 3
            .lineTo((flange_c - shield_c) / 2, -(center + gap_right))  # SECTION 3
            .lineTo(shield_c + (flange_c - shield_c) / 2, -(center + gap_right))  # SECTION 3
            .lineTo(flange_c, -center)  # SECTION 3
            .lineTo(flange_c, 0)  # SECTION 2
            .close()
            ).add(arc)

    cq.exporters.exportDXF(jack, 'sheet.dxf')


def get_valve_stp(*, flange_c, pipe_c, shield_c, valve_l, valve_c, gap_left, gap_right, actuator_gap, thck, bolts_num=8,
                  bolts_d=5, actuator_type='electric', path='valve.step'):
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

    build(r_flange, l_flange, bdy, path)


if __name__ == '__main__':
    get_valve_stp(flange_c=500  # circumference of the flange (REQUIRED)
                  , valve_l=280  # length of the valve (REQUIRED)
                  , shield_c=460  # circumference of the shield (REQUIRED)
                  , pipe_c=240  # circumference of the pipe (REQUIRED)
                  , valve_c=500  # circumference of the valve (top side) (REQUIRED)
                  , gap_left=80  # gap btw flange and shield (left) (REQUIRED)
                  , gap_right=50  # gap btw flange and shield (right) (REQUIRED)
                  , thck=20  # thickness of the flange (REQUIRED)
                  , actuator_gap=200  # gap from the edge of actuator and outter flange (OPTIONAL)
                  , path='H:\\Desktop\\valve2.step'  # path where the file will be saved. Default: 'valve.step'
                  # , bolts_num= # amount of holes in a flange, by default 8 (OPTIONAL)
                  # , bolts_d= # hole diameter, by default 5 (OPTIONAL)
                  )
