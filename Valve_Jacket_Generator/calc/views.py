import os
from .models import ValveParams
from .forms import UserInputForm
from django.shortcuts import render, redirect
from .valve_jacket_v1 import get_jacket_dxf, get_valve_stp, get_zip
from django.http import Http404, HttpResponse

def start(request):
    return render(request, 'index.html')

# def user_input(request):
#     if request.method == 'POST':
#         form = UserInputForm(request)
#         if form.is_valid():
#             form.save()
#             return redirect('gen_file')
#     else:
#         form = UserInputForm()
#     return render(request, 'index.html', {'form': form})


def download_file(request):
    file_path = 'C:\\Users\\pangl\\mysite\\Valve_modelling\\Valve_Jacket_Generator\\calc\\temp\\files.zip'  # Replace with the actual path to your file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404


def gen_file(request):
    if request.method == 'POST':
        flange_c = float(request.POST['flange_c'])
        flange_thck = float(request.POST['flange_thck'])
        shield_c = float(request.POST['shield_c'])
        valve_c = float(request.POST['valve_c'])
        valve_l = float(request.POST['valve_l'])
        gap_left = float(request.POST['gap_left'])
        gap_right = float(request.POST['gap_right'])
        pipe_c = float(request.POST['pipe_c'])
        X_offset = float(request.POST['X_offset'])
        Y_offset = float(request.POST['Y_offset'])
        hole_offset = float(request.POST['hole_offset'])

        step_path = 'C:\\Users\\pangl\\mysite\\Valve_modelling\\Valve_Jacket_Generator\\calc\\temp\\valve_3d.step'
        dxf_path = 'C:\\Users\\pangl\\mysite\\Valve_modelling\\Valve_Jacket_Generator\\calc\\temp\\drawing.dxf'

        # GETTING A 3D MODEL OF VALVE (output is .step file)
        get_valve_stp(flange_c=flange_c
                      , valve_l=valve_l
                      , shield_c=shield_c
                      , pipe_c=pipe_c
                      , valve_c=valve_c
                      , gap_left=gap_left
                      , gap_right=gap_right
                      , thck=flange_thck
                      , path_step=step_path
                      , actuator_gap=0
                      # , bolts_num=bolts_num
                      )

        # GETTING A 2D SKETCH OF THE JACKET FOR A VALVE (output is .dxf file)
        get_jacket_dxf(flange_c=flange_c
                       , valve_l=valve_l
                       , shield_c=shield_c
                       , valve_c=valve_c
                       , gap_left=gap_left
                       , gap_right=gap_right
                       , thck=flange_thck
                       , X_offset=X_offset
                       , Y_ofst=Y_offset # fix it
                       , hole_offset=hole_offset
                       , path_sketch=dxf_path
                       )

        get_zip(path_1=step_path
                , path_2=dxf_path
                , zip_path='C:\\Users\\pangl\\mysite\\Valve_modelling\\Valve_Jacket_Generator\\calc\\temp\\files.zip')

        file_path = 'C:\\Users\\pangl\\mysite\\Valve_modelling\\Valve_Jacket_Generator\\calc\\temp\\files.zip'  # Replace with the actual path to your file
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                return response
        else:
            raise Http404
