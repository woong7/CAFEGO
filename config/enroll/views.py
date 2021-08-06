from django.shortcuts import render

# Create your views here.

def enroll_home(request):
    return render(request, "enroll/home.html")

def enroll_new_cafe(request):
    return render(request, "enroll/new_cafe.html")

def enroll_visited_cafe(request):
    return render(request, "enroll/visited_cafe.html")
