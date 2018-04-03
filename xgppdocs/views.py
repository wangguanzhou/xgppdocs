from django.shortcuts import render
import os.path

SA2Meetings = [
    {'name': 'SA2-126', 'time': 'Feb 2018', 'city': 'Montreal',},
    {'name': 'SA2-125', 'time': 'Jan 2018', 'city': 'Gothenburg',},
]

def homepage(request):
    context = {}
    context['sa2meetings'] = SA2Meetings
    return render(request, 'homepage.html', context)