import cadquery as cq
from math import sin, cos, radians, pi
from zipfile import ZipFile
from os import remove


class ValveJacket:
    def __init__(self, *, flange_c: float, pipe_c: float
                 , gap_left: float, gap_right: float, shield_c: float
                 , valve_c: float, valve_l: float, thck: float = 5
                 , bolts_num: int = 8, bolts_d: float = 5
                 , x_offset: float, y_offset: float, hole_offset: float
                 , step_path: str, dxf_path: str, zip_path):
        self.flange_c = flange_c  # circumference of the flange (REQUIRED)
        self.pipe_c = pipe_c  # circumference of the pipe (REQUIRED)
        self.gap_left = gap_left  # gap btw flange and shield (left) (REQUIRED)
        self.gap_right = gap_right  # gap btw flange and shield (right) (REQUIRED)
        self.shield_c = shield_c  # circumference of the shield (REQUIRED)
        self.valve_c = valve_c  # circumference of the valve (top side) (REQUIRED)
        self.valve_l = valve_l  # length of the valve (REQUIRED)
        self.thck = thck  # thickness of the flange (REQUIRED)
        self.bolts_num = bolts_num  # number of bolts in the flange
        self.bolts_d = bolts_d  # hole diameter, by default 5 (OPTIONAL)
        self.x_offset = x_offset  # Offset for increasing the width. Zero by default. (OPTIONAL)
        self.y_offset = y_offset  # Offset for increasing the length. Zero by default. (OPTIONAL)
        self.hole_offset = hole_offset  # Offset for increasing the hole diameter. Zero by default. (OPTIONAL)

        # Paths (have to be configured for django)
        self.step_path = step_path
        self.dxf_path = dxf_path
        self.zip_path = zip_path

        self.__left_side = False  # Internal variable for flange_c function

    def __flanges(self, left_side):
        """
        GENERATES TWO FLANGES WITH PIPE AND SHIELD
        WORKS BOTH FOR LEFT AND RIGHT SIDE
        """
        # try:
        # GET DIAMETER
        flange_d = self.flange_c / pi
        pipe_d = self.pipe_c / pi
        shield_d = self.shield_c / pi

        # ERROR CATCHING
        if pipe_d >= flange_d:
            raise ValueError('"pipe_c" cannot be greater than or equal to "flange_c"')
        elif (flange_d - pipe_d) <= self.bolts_d:
            raise ValueError('Holes do not fit this flange. Make holes smaller ("bolts_d") or increase "flange_d"')

        # BASE CYLINDER
        base = cq.Workplane("XZ").cylinder(self.thck, flange_d)

        # CENTER HOLE
        front_face = cq.Workplane("XZ").workplane(offset=self.thck).moveTo(0, 0)
        sketch = front_face.circle(pipe_d).extrude(-self.thck * 2)
        result = base.cut(sketch)

        # SMALL HOLES
        ofst = pipe_d + ((flange_d - pipe_d) / 2)
        for i in range(self.bolts_num):
            angle = i * (360 / self.bolts_num)
            x = ofst * cos(radians(angle))
            y = ofst * sin(radians(angle))
            front_face = cq.Workplane("XZ").workplane(offset=self.thck).moveTo(x, y)
            sketch = front_face.circle(self.bolts_d).extrude(-self.thck * 2)
            result = result.cut(sketch)

        # MIRRORING THE FLANGES
        result = result.translate(result.val().BoundingBox().center.multiply(-1))
        mirxz_neg = result.mirror(mirrorPlane="XZ", basePointVector=(0, (self.thck / 2) + 0.1, 0))
        result = result.union(mirxz_neg)

        # PIPE WITH THE SHIELD
        face, coef, gap = "<Y", 1, self.gap_right
        if left_side:
            face, coef, gap = ">Y", -1, self.gap_left

        result = (result
                  .faces(face)
                  .circle(pipe_d)
                  .extrude(gap / coef)
                  .faces(face)
                  .circle(shield_d)
                  .extrude(700 / coef)
                  )

        return result

    def __body(self):
        # Get diameter
        flange_d = self.flange_c / pi
        pipe_d = self.pipe_c / pi
        valve_d = self.valve_c / pi

        if valve_d >= self.valve_l:
            raise ValueError('"valve_c" cannot be greater than or equal to "valve_l"')

        # Get length of body excluding the flange thickness
        total = self.valve_l - (self.thck * 4)  # flange is always 50mm

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

    def __build(self, *, right_flange, left_flange, bdy, path_step='valve.step'):
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

    def get_valve_stp(self):
        r_flange = self.__flanges(left_side=False)

        l_flange = self.__flanges(left_side=True)

        bdy = self.__body()

        self.__build(right_flange=r_flange, left_flange=l_flange, bdy=bdy, path_step=self.step_path)

    def get_jacket_dxf(self):
        valve_d = round(self.valve_c / pi, 3)
        center = self.valve_l - (2 * self.thck)  # THE LENGTH OF THE CENTER SIDE (BODY OF VALVE)

        # OFFSETS
        valve_d += self.hole_offset  # Increasing the hole

        self.gap_left += self.x_offset  # (X axis) increasing the left gap
        self.gap_right += self.x_offset  # (X axis) increasing the right gap

        self.flange_c += self.y_offset  # (Y axis) increasing circumference depending on a thck of jacket (MIDDLE SIDE)
        self.shield_c += self.y_offset  # (Y axis) increasing circumference depending on a thck of jacket (TOP SIDES)

        # FOR FINDING THE HOLE COORDINATES
        center_hole = (center - valve_d) / 2

        # VARIABLES FOR ARCS
        # First point of the ThreePointArc is defined by the last drawn line
        arc1_p2 = (valve_d / 2, -(center_hole + (valve_d / 2)))
        arc1_p3 = (0, -(center_hole + valve_d))
        arc2_p2 = ((self.flange_c - (valve_d / 2)), -(center / 2))
        arc2_p3 = (self.flange_c, -center_hole)

        # CREATING SKETCH
        jack = (cq.Workplane("XY")
                .moveTo(0.0)  # STARTING POINT
                .lineTo(self.flange_c, 0.0)  # SECTION 1
                .lineTo(self.shield_c + (self.flange_c - self.shield_c) / 2, self.gap_left)  # SECTION 1
                .lineTo((self.flange_c - self.shield_c) / 2, self.gap_left)  # SECTION 1
                .lineTo(0.0, 0.0)  # SECTION 1
                .lineTo(0, -center_hole)  # SECTION 2 (part 1)
                .threePointArc(arc1_p2, arc1_p3)  # SECTION 2 (part 1)
                .lineTo(0, -center)  # SECTION 2 (part 1)
                .lineTo(self.flange_c, -center)  # SECTION 3
                .moveTo(0, -center)  # MOVING THE WORKING POSITION
                .lineTo((self.flange_c - self.shield_c) / 2, -(center + self.gap_right))  # SECTION 3
                .lineTo(self.shield_c + (self.flange_c - self.shield_c) / 2, -(center + self.gap_right))  # SECTION 3
                .lineTo(self.flange_c, -center)  # SECTION 3
                .lineTo(self.flange_c, -(center_hole + valve_d))  # SECTION 2 (part 2)
                .threePointArc(arc2_p2, arc2_p3)  # SECTION 2 (part 2)
                .lineTo(self.flange_c, 0)  # SECTION 2 (part 2)
                .close()
                )

        return cq.exporters.exportDXF(jack, self.dxf_path)

    def get_zip(self):
        # Creating a ZipFile object
        zipObj = ZipFile(self.zip_path, 'w')

        # Writing files to zipfile
        zipObj.write(self.step_path)
        zipObj.write(self.dxf_path)

        zipObj.close()

        # Removing the files that were saved to the zipfile
        remove(self.step_path)
        remove(self.dxf_path)



