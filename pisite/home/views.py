from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from home.forms import UploadSoundForm

import os
import subprocess

# Create your views here.
def index(request):
  context = {}
  return render(request, 'home/index.html', context)

def uploadSound(request):
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
  return render(request, 'home/uploadSound.html', context)