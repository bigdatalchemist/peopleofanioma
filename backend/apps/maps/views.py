from django.shortcuts import render

def map_home(request):
    return render(request, 'maps/anioma_partial_map.html')
