from django.shortcuts import render

# Create your views here.
def maps_test(request):
    return render(request, 'maps/test.html')