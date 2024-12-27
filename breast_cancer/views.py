from django.shortcuts import render
from rest_framework.decorators import api_view

@api_view(["GET"])
def render_project(request):
    return render(request, 'BREAST_CANCER.html')
