from django.shortcuts import render

# Create your views here.
class home:
    def index(request):
        return render(request, "index.html")