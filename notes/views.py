from django.shortcuts import HttpResponse
from django.template import loader
# Create your views here.
def members(request):
    template = loader.get_template('notes/resume.html')
    return HttpResponse(template.render())