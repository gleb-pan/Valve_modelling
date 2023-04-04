import os
from .models import ValveParams
from django.shortcuts import render
from .valve_jacket_v1 import get_jacket_dxf, get_valve_stp, get_zip
from .valve_jacket_v2 import ValveJacket
from django.http import Http404, HttpResponse

def start(request):
    return render(request, 'index.html')


def gen_file(request):
    if request.method == 'POST':
        # GETTING THE VALVE AND JACKET PARAMETERS
        p_flange_c = float(request.POST['flange_c'])
        p_flange_thck = float(request.POST['flange_thck'])
        p_shield_c = float(request.POST['shield_c'])
        p_valve_c = float(request.POST['valve_c'])
        p_valve_l = float(request.POST['valve_l'])
        p_gap_left = float(request.POST['gap_left'])
        p_gap_right = float(request.POST['gap_right'])
        p_pipe_c = float(request.POST['pipe_c'])
        p_x_offset = float(request.POST['X_offset'])
        p_y_offset = float(request.POST['Y_offset'])
        p_hole_offset = float(request.POST['hole_offset'])

        # CREATING A ValveJacket OBJECT
        jacket_files = ValveJacket(flange_c=p_flange_c
                                   , thck=p_flange_thck
                                   , shield_c=p_shield_c
                                   , valve_c=p_valve_c
                                   , valve_l=p_valve_l
                                   , gap_left=p_gap_left
                                   , gap_right=p_gap_right
                                   , pipe_c=p_pipe_c
                                   , x_offset=p_x_offset
                                   , y_offset=p_y_offset
                                   , hole_offset=p_hole_offset
                                   )

        db_write = ValveParams(date=jacket_files.db_timestamp
                               , flange_c=p_flange_c
                               , flange_thck=p_flange_c
                               , shield_c=p_shield_c
                               , valve_c=p_valve_c
                               , valve_l=p_valve_l
                               , gap_left=p_gap_left
                               , gap_right=p_gap_right
                               , pipe_c=p_pipe_c
                               , X_offset=p_x_offset
                               , Y_offset=p_y_offset
                               , hole_offset=p_hole_offset
                               )
        db_write.save()

        # GENERATING FILES AND PROVIDING THE PATH TO A FILE
        file_path = jacket_files.get_everything()  # method 'get_everything' returns the path

        # SENDING FILE AS DOWNLOAD
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                return response
        else:
            raise Http404
