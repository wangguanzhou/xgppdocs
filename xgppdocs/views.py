from django.shortcuts import render
import os

SA2Meetings = [
    {'name': 'SA2-126', 'time': 'Feb 2018', 'city': 'Montreal',},
    {'name': 'SA2-125', 'time': 'Jan 2018', 'city': 'Gothenburg',},
]

TDOC_ROOT = '/var/www/xgppdocs/tdocs/'

def homepage(request):
    context = {}
    context['sa2meetings'] = SA2Meetings
    return render(request, 'homepage.html', context)

def showtdoclist(request):
    context = {}
    context['sa2meetings'] = SA2Meetings
    if request.GET:
        meeting_no = request.GET['meeting']
        tdoc_list = get_tdoc_list(meeting_no)
        context['meeting_no'] = meeting_no
        context['tdoc_list'] = tdoc_list
        return render(request, 'tdoclist.html', context)
        
def get_tdoc_list(meeting_no):
    tdoc_path = TDOC_ROOT + '/' + meeting_no
    if os.path.isdir(tdoc_path):
        return tdoc_path
    else:
        try:
            os.makedirs(tdoc_path)
        except:
            raise
        return tdoc_path


