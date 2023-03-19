from django.shortcuts import render
from .valve_jacket_v1 import get_jacket_dxf, get_valve_stp, get_zip


def index(request):
    return render(request, 'index.html')


def gen_file(request):
    if request.method == 'POST':
        flange_c = request.POST['flange_c']
        flange_thck = request.POST['flange_thck']
        shield_c = request.POST['shield_c']
        valve_c = request.POST['valve_c']
        valve_l = request.POST['valve_l']
        gap_left = request.POST['gap_left']
        gap_right = request.POST['gap_right']
        pipe_c = request.POST['pipe_c']

        # GETTING A 3D MODEL OF VALVE (output is .step file)
        get_valve_stp(flange_c=flange_c
                      , valve_l=valve_l
                      , shield_c=shield_c
                      , pipe_c=pipe_c
                      , valve_c=valve_c
                      , gap_left=gap_left
                      , gap_right=gap_right
                      , thck=thck
                      , actuator_gap=actuator_gap
                      # , bolts_num=bolts_num
                      , bolts_d=bolts_d
                      , path_step=path_step
                      )

        # GETTING A 2D SKETCH OF THE JACKET FOR A VALVE (output is .dxf file)
        get_jacket_dxf(flange_c=flange_c
                       , valve_l=valve_l
                       , shield_c=shield_c
                       , valve_c=valve_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , thck=thck
                       , X_offset=X_offset
                       , Y_ofst=Y_ofst
                       , hole_offset=hole_offset
                       , path_sketch=path_sketch
                       )

        get_zip(path_1=path_step, path_2=path_sketch, zip_path='H:\\Desktop\\files.zip')

        return render(request, 'index.html')
