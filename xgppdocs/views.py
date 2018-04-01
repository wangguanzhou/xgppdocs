from django.shortcuts import render
import os.path


def homepage(request):
    return render(request, 'homepage.html', {})