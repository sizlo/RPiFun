# Uses a motion sensor on the GPIO and plays a random ogg file from a selection
# when active

# ==============================================================================
# Imports
# ------------------------------------------------------------------------------
from pygame import mixer
import time
import sys
import getopt
import logging
import random
import glob
import datetime

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing GPIO. Are you running under sudo?")

# ==============================================================================
# Global variables
# ------------------------------------------------------------------------------
debugMode = False
userTriggerMode = False
secondsToWaitAfterSound = 5
inputChannel = 7
timeout = 15
earliest = 10
latest = 24
initialPercentChance = 20
percentChance = initialPercentChance
percentChanceIncrement = 5
maxPercentChance = 100
usageText = """Usage: """ + sys.argv[0] + """ [-d|--debug] [--userTrigger] [-w|--wait seconds] [-t|--timeout seconds] [-e|--earliest hour] [-l|--latest hour] [-c|--chance percent] [-i|--increment percent] [-m|--maxChance percent] [-h|--help]

OPTIONS
\t-d --debug
\t\tRun in debug mode (show more detailed output)

\t--userTrigger
\t\tTake user input as the trigger instead of the motion sensor

\t-w --wait seconds
\t\tThe number of seconds to wait after each sound plays

\t-t --timeout seconds
\t\tThe number of seconds to cut off a sound after

\t-e --earliest hours
\t\tThe earliest hour the program is allowed to play sound in 24hr format
\t\tE.g """ + sys.argv[0] + """ -e 14
\t\tWill not allow sounds to be played before 2pm

\t-l --latest hourse
\t\tThe latest hour the program is allowed to play sound in 24hr format
\t\tE.g """ + sys.argv[0] + """ -e 14
\t\tWill not allow sounds to be played after 2pm

\t-c --chance percent
\t\tThe initial percentage chance that a sound will play when motion is detected

\t-i --increment percent
\t\tThe percentage to increment the chance to play by

\t-m --maxChance percent
\t\tThe maximum that the chance to play can get to

\t-h --help
\t\tShow this message"""

# ==============================================================================
# Exit the program with a message
# ------------------------------------------------------------------------------
def exitWithMessage(msg):
  print msg
  sys.exit(0)

# ==============================================================================
# Parse command line arguments
# ------------------------------------------------------------------------------
def parseArgs():
  # Use globals
  global debugMode
  global userTriggerMode
  global secondsToWaitAfterSound
  global usageText
  global timeout
  global earliest
  global latest
  global initialPercentChance
  global percentChance
  global percentChanceIncrement
  global maxPercentChance

  try:
    # Get the list of options provided, and there args
    opts, args = getopt.getopt(sys.argv[1:], "dw:t:e:l:c:h",["debug", "userTrigger", "wait=", "timeout=", "earliest=", "latest=", "chance=", "help"])
  except getopt.GetoptError:
    # Print usage and exit on unknown option
    exitWithMessage(usageText)

  # Loop through and react to each option
  for opt, arg in opts:
    if opt in ("-d", "--debug"):
      debugMode = True
    elif opt in ("--userTrigger"):
      userTriggerMode = True
    elif opt in ("-w", "--wait"):
      secondsToWaitAfterSound = float(arg)
    elif opt in ("-t", "--timeout"):
      timeout = int(arg)
    elif opt in ("-e", "--earliest"):
      earliest = int(arg)
    elif opt in ("-l", "--latest"):
      latest = int(arg)
    elif opt in ("-c", "--chance"):
      initialPercentChance = int(arg)
      percentChance = initialPercentChance
    elif opt in ("-i", "--increment"):
      percentChanceIncrement = int(arg)
    elif opt in ("-m", "--maxChance"):
      maxPercentChance = int(arg)
    elif opt in ("-h", "--help"):
      exitWithMessage(usageText)

# ==============================================================================
# Setup the GPIO
# ------------------------------------------------------------------------------
def setupGPIO():
  # Use globals
  global inputChannel

  # Set the pin numbering mode
  GPIO.setmode(GPIO.BOARD)

  # Setuo the channels
  GPIO.setup(inputChannel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  logging.debug("Channel %d set to input", inputChannel)

# ==============================================================================
# Initialise the program
# ------------------------------------------------------------------------------
def init():
  # We want to use the global debugMode
  global debugMode

  # Parse the command line arguments to the program
  parseArgs()

  # Initialise root logger
  lvl = logging.INFO
  if debugMode:
    lvl = logging.DEBUG
  formatString = "%(levelname)-8s %(asctime)s %(funcName)s:%(lineno)s: %(message)s"
  formatter = logging.Formatter(formatString)
  logging.basicConfig(level=lvl, format=formatString)

  # Initialise the file logging
  fileHandle = logging.FileHandler("motionSound.log")
  fileHandle.setLevel(logging.INFO)
  fileHandle.setFormatter(formatter)
  logging.getLogger().addHandler(fileHandle)

  logging.debug("Initialising")

  # Initialise GPIO
  setupGPIO()

  # Initialise the mixer
  mixer.init()

# ==============================================================================
# Clean up the program
# ------------------------------------------------------------------------------
def cleanup():
  logging.debug("Cleaning up")

  # Cleanup GPIO
  GPIO.cleanup()
  

# ==============================================================================
# Start playing a sound file
# ------------------------------------------------------------------------------
def startFile(theFileName):
  logging.info("Playing %s", theFileName)
  mixer.music.load(theFileName)
  mixer.music.play()

# ==============================================================================
# Start playing a random song
# ------------------------------------------------------------------------------
def startRandomFile():
  # Build a list of ogg files in this directory
  fileNames = glob.glob("*.ogg")
  # Choose a random file from this list
  fileName = random.choice(fileNames)
  startFile(fileName)

# ==============================================================================
# Wait for the playing music to finish
# ------------------------------------------------------------------------------
def waitForCurrentFile():
  # Use globals
  global timeout

  # Ensure we cut off playback after a timeout
  startTime = time.time()
  cutoffTime = startTime + timeout
  while mixer.music.get_busy():
    # Sleep for a second
    time.sleep(1)
    # If it's been 15s stop playback
    currentTime = time.time()
    if currentTime > cutoffTime:
      mixer.music.stop()
      logging.debug("Music cut off after %ds" % (timeout))
  logging.debug("Music finished")

# ==============================================================================
# Wait for the motion sensor to trigger
# ------------------------------------------------------------------------------
def waitForTrigger():
  # Use globals
  global userTriggerMode
  global inputChannel

  if userTriggerMode:
    # In user trigger mode wait for user input
    raw_input("Press enter to trigger")
    logging.info("Triggered by user input")
  else:
    # Wait for the motion sensor GPIO to go high
    logging.debug("Waiting for motion sensor")
    # Add an event detect for the edge we want
    GPIO.add_event_detect(inputChannel, GPIO.RISING)
    # Wait for that event
    while not GPIO.event_detected(inputChannel):
      time.sleep(1)
    logging.info("Motion detected")
    # Remove the event detect
    GPIO.remove_event_detect(inputChannel)

# ==============================================================================
# Decide whether we should pla a file or not
# ------------------------------------------------------------------------------
def shouldPlayFile():
  # Use globals
  global earliest
  global latest
  global initialPercentChance
  global percentChance
  global percentChanceIncrement
  global maxPercentChance

  # If it's outside the allowed time then don't play
  currentTime = datetime.datetime.now()
  if currentTime.hour < earliest:
    logging.info("Too early to play sound")
    return False
  if currentTime.hour >= latest:
    logging.info("Too late to play sound")
    return False

  # Only play a sound a certain percentage of the time
  generatedNum = random.randint(1, 100)
  if generatedNum > percentChance:
    logging.debug("Generated %d, must be %d or lower" % (generatedNum, percentChance))
    # Increment the chance to play
    percentChance = percentChance + percentChanceIncrement
    percentChance = min(percentChance, maxPercentChance)
    logging.info("Chance to play is now %d%%" % (percentChance))
    return False

  # Reset the chance to play since we're going to play now
  percentChance = initialPercentChance

  return True

# ==============================================================================
# Program entry / main
# ------------------------------------------------------------------------------
def main():
  # Use globals
  global secondsToWaitAfterSound

  init()

  try:
    while True:
      waitForTrigger()
      if shouldPlayFile():
        startRandomFile()
        waitForCurrentFile()
      # Wait to make sure we don't spam sound
      if secondsToWaitAfterSound > 0:
        logging.debug("Waiting %f seconds", secondsToWaitAfterSound)
        time.sleep(secondsToWaitAfterSound)
  except KeyboardInterrupt:
    logging.debug("Keyboard interrup caught")
    cleanup()



main()
