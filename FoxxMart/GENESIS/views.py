from django.shortcuts import render

# Create your views
def store(request):

    return render (request, 'genesis_base.html', {})
