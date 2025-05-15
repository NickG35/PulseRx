from django.shortcuts import render

# Create your views here.
def pharmacy_home(request):
    return render(request, 'pharmacy_home.html')