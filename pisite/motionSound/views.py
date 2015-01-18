from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from logs.forms import LineCountForm
from home.forms import UploadSoundForm
from motionSound.models import TextFile

import os
import subprocess
import ConfigParser

def strToBool(configStr):
  states = {  '1': True, 'yes': True, 'true': True, 'on': True, 'True': True,
              '0': False, 'no': False, 'false': False, 'off': False, 'False': False}
  return states[configStr]

def boolToStr(configBool):
  if configBool:
    return "true"
  else:
    return "false"

# Create your views here.
def index(request):
  configFile = get_object_or_404(TextFile, name="config")
  configFilePath = settings.BASE_DIR + "/" + configFile.filePath
  config = ConfigParser.RawConfigParser()
  config.read(configFilePath)
  soundDisabled = strToBool(config.get("misc", "sounddisabled"))

  # Handle POST
  if request.method == 'POST':
    # The toggle sound button was clicked, edit the config file
    soundDisabled = not soundDisabled
    config.set("misc", "sounddisabled", boolToStr(soundDisabled))
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

def upload(request):
  # Handle POSTs
  if request.method == 'POST':
    # Populate a form with the given data
    form = UploadSoundForm(request.POST, request.FILES)

    # If the form is valid process the file
    if form.is_valid():
      soundFile = request.FILES['sound']
      fileName = soundFile.name

      # Write the file to /tmp
      data = soundFile.read()
      tmpFile = open("/tmp/" + fileName, 'w')
      tmpFile.write(data)
      tmpFile.close()

      # Convert to ogg
      inputFileName = fileName
      outputFileName = fileName
      # Replace the extention with .ogg
      name, ext = os.path.splitext(outputFileName)
      outputFileName = name + ".ogg"
      # Get timings
      startTime = form.cleaned_data['startTime']
      duration = form.cleaned_data['duration']
      # Call ffmpeg
      if inputFileName != outputFileName:
        command = ["ffmpeg",
                  "-i", "/tmp/" + inputFileName,
                  "-ss", startTime,
                  "-t", duration,
                  "-y",
                  "-acodec", "libvorbis",
                  "/tmp/" + outputFileName]
        try:
          subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
          errorMsg = "Error converting to ogg with command: " + str(e.cmd) + "\n"
          errorMsg += "Return code was: " + str(e.returncode) + "\n"
          errorMsg += "Output was:\n" + str(e.output)
          return HttpResponse(errorMsg)

      # Move to the MotionSound dir
      directory = settings.BASE_DIR + "/../MotionSound/"
      if os.path.exists(directory + outputFileName):
        return HttpResponse(outputFileName + " already exists, use a different file name")
      command = ["mv", "-n", "/tmp/" + outputFileName, directory + "."]
      try:
        subprocess.check_output(command)
      except subprocess.CalledProcessError as e:
        errorMsg = "Error moving to directory with command: " + str(e.cmd) + "\n"
        errorMsg += "Return code was: " + str(e.returncode) + "\n"
        errorMsg += "Output was:\n" + str(e.output)
        return HttpResponse(errorMsg)

      # Everything worked
      return HttpResponse(inputFileName + " succesfully uploaded and converted to " + outputFileName)

    # Handle invald form
    else:
      return HttpResponse("Unknown error, the recieved form is not valid")

  # Handle normal methods
  else:
    form = UploadSoundForm()

  context = {'form': form}
  return render(request, 'motionSound/upload.html', context)