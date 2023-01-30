#pip install --pre git+https://github.com/CadQuery/cadquery.git

import math
import cadquery as cq
from cadquery import Workplane


def flanges(*, valve_l, flange_c, pipe_c, gap_left, gap_right, shield_c, thck=50, left_side=False, bolts_num=8,
            bolts_d=60):
    '''
    GENERATES TWO FLANGES WITH PIPE AND SHIELD
    WORKS BOTH FOR LEFT AND RIGHT SIDE
    '''

    # GET DIAMETER
    flange_d = flange_c / math.pi
    pipe_d = pipe_c / math.pi
    shield_d = shield_c / math.pi

    # ERROR CATCHING
    if pipe_d >= flange_d:
        raise ValueError('"pipe_c" cannot be greater than or equal to "flange_c"')
    elif (flange_d - pipe_d) <= bolts_d:
        raise ValueError('Holes do not fit this flange. Make holes smaller or increase "flange_d"')

    # BASE CYLINDER
    base = Workplane("XZ").cylinder(thck, flange_d)

    # CENTER HOLE
    front_face = Workplane("XZ").workplane(offset=thck).moveTo(0, 0)
    sketch = front_face.circle(pipe_d).extrude(-thck * 2)
    result = base.cut(sketch)

    # SMALL HOLES
    ofst = pipe_d + ((flange_d - pipe_d) / 2)
    for i in range(bolts_num):
        angle = i * (360 / bolts_num)
        x = ofst * math.cos(math.radians(angle))
        y = ofst * math.sin(math.radians(angle))
        front_face = Workplane("XZ").workplane(offset=thck).moveTo(x, y)
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

    # result.val().exportStep('res.stp')
    # show_object(result)
    return result


def body(*, valve_l=1100, flange_c=2820, pipe_c=1950, valve_c=800):
    # Get diameter
    flange_d = flange_c / math.pi
    pipe_d = pipe_c / math.pi
    valve_d = valve_c / math.pi

    # Get length of body excluding the flange thickness
    total = valve_l - 200  # flange is always 50mm

    side = (total - valve_d) / 2

    bdy = (cq
           .Workplane("XZ").move(0, 0)
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


def build(right_flange, left_flange, body):
    valve = (cq.Assembly()
             .add(right_flange
                  , name="right"
                  , color=cq.Color("lightgray")
                  )
             .add(left_flange
                  , name="left"
                  , color=cq.Color("lightgray")
                  )
             .add(body
                  , name="body"
                  , color=cq.Color("lightgray")
                  )
             )

    (valve
     .constrain("right@faces@>Y", "body@faces@<Y", "Plane")
     .constrain("body@faces@>Y", "left@faces@<Y", "Plane")
     )

    valve.solve()

    user = input("Do you wish to save this valve?(y\\n)")
    if user == 'y':
        valve.save('H:\\Desktop\\valve.step') #PATH WHERE THE FILE WILL BE SAVED
        print("Saved as 'valve.step'")
    print('\nProgram finished')


def get_valve_stp(*, flange_c, pipe_c, shield_c, valve_l, valve_c, gap_left, gap_right, actuator_gap,
                  actuator_type='electric'):
    r_flange = flanges(valve_l=valve_l
                       , flange_c=flange_c
                       , pipe_c=pipe_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , shield_c=shield_c
                       , left_side=False
                       )

    l_flange = flanges(valve_l=valve_l
                       , flange_c=flange_c
                       , pipe_c=pipe_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , shield_c=shield_c
                       , left_side=True
                       )

    bdy = body(valve_l=valve_l
               , flange_c=flange_c
               , pipe_c=pipe_c
               , valve_c=valve_c
               )

    build(r_flange, l_flange, bdy)

'''
 flange_c - circumference of the flange
 pipe_c - circumference of the pipe
 shield_c - circumference of the shield
 valve_l - length of the valve
 valve_c - circumference of the valve(top side)
 gap_left - gap btw flange and shield(left)
 gap_right - gap btw flange and shield(right)
 actuator_gap - distance btw actuator and flange
 actuator_type - electric, manual or other
 actuator_l - length of the actuator (actuator_type: other)
'''

#MAIN
if __name__=='__main__':
    get_valve_stp(actuator_gap=200
                      , flange_c=2820
                      , valve_l=1100
                      , shield_c=2750
                      , pipe_c=1950
                      , valve_c=800
                      , gap_left=350
                      , gap_right=310
                  )