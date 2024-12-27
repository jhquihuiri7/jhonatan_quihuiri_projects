from django.shortcuts import render
from rest_framework.decorators import api_view

@api_view(["GET"])
def render_project_darwin_finches(request):
    return render(request, 'DARWIN_FINCHES.html')
