from django.shortcuts import render, get_object_or_404

from logs.models import Log

# Create your views here.
def index(request):
  logList = Log.objects.all()
  context = {'logList': logList}
  return render(request, 'logs/index.html', context)

def log(request, logName):
  log = get_object_or_404(Log, name=logName)
  context = {'log': log}
  return render(request, 'logs/log.html', context)