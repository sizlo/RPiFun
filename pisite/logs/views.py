from django.shortcuts import render, get_object_or_404

from logs.models import Log
from logs.forms import LineCountForm

# Create your views here.
def index(request):
  logList = Log.objects.all()
  context = {'logList': logList}
  return render(request, 'logs/index.html', context)

def log(request, logName):
  lineCount = Log.defaultLinesToShow
  # Handle POSTS
  if request.method == 'POST':
    form = LineCountForm(request.POST)
    if form.is_valid():
      lineCount = form.cleaned_data['linesToFetch']
  else:
    form = LineCountForm()

  log = get_object_or_404(Log, name=logName)
  logText = log.getLastNLines(n=lineCount)

  context = {'logName': log.name, 'logText': logText, 'form': form}
  return render(request, 'logs/log.html', context)