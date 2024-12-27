from django.shortcuts import render

# Create your views here.
def render_google_project(request):
    return render(request,"dashboard.html")
