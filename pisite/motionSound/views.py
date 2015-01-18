from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from logs.forms import LineCountForm
from motionSound.models import TextFile

import subprocess
import ConfigParser

# Create your views here.
def index(request):
  configFile = get_object_or_404(TextFile, name="config")
  configFilePath = settings.BASE_DIR + "/" + configFile.filePath
  config = ConfigParser.RawConfigParser()
  config.read(configFilePath)
  soundDisabled = config.getboolean("misc", "sounddisabled")

  # Handle POST
  if request.method == 'POST':
    # The toggle sound button was clicked, edit the config file
    soundDisabled = not soundDisabled
    config.set("misc", "sounddisabled", soundDisabled ? "true" : "false")
    with open(configFilePath, "wb") as configfile:
      config.write(configfile)

  log = get_object_or_404(TextFile, name="log")
  logText = log.getLastNLines(n=TextFile.defaultLinesToShow)

  configText = configFile.getFileContents()

  # Check if the script is running
  # Simply check the return code of a ps aux into grep
  running = "Yes"
  try:
    ps = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
    subprocess.check_call(["grep", "[m]otionSound"], stdin=ps.stdout)
    ps.wait()
  except subprocess.CalledProcessError as e:
    if e.returncode == 1:
      running = "No"

  # Check if sound is disabled in the config
  soundEnabled = "Yes"
  if soundDisabled:
    soundEnabled = "No"

  context = { 'logText': logText, 
              'configText': configText, 
              'running': running,
              'soundEnabled': soundEnabled}
  return render(request, 'motionSound/index.html', context)

def log(request):
  lineCount = TextFile.defaultLinesToShow
  # Handle POSTS
  if request.method == 'POST':
    form = LineCountForm(request.POST)
    if form.is_valid():
      lineCount = form.cleaned_data['linesToFetch']
  else:
    form = LineCountForm()

  log = get_object_or_404(TextFile, name="log")
  logText = log.getLastNLines(n=lineCount)

  context = {'logText': logText, 'form': form}
  return render(request, 'motionSound/log.html', context)

def config(request):
  config = get_object_or_404(TextFile, name="config")
  configText = config.getFileContents()
  context = {'configText': configText}
  return render(request, 'motionSound/config.html', context)