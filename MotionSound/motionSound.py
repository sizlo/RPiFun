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
fileNames = ["cenashort.ogg", "zaynshort.ogg", "watchasay.ogg", "wildcard.ogg"]
usageText = """Usage: """ + sys.argv[0] + """ [-d|--debug] [--userTrigger] [-w|--wait seconds] [-h|--help]

OPTIONS
\t-d --debug
\t\tRun in debug mode (show more detailed output)

\t--userTrigger
\t\tTake user input as the trigger instead of the motion sensor

\t-w --wait seconds
\t\tThe number of seconds to wait after each sound plays

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

  try:
    # Get the list of options provided, and there args
    opts, args = getopt.getopt(sys.argv[1:], "dw:h",["debug", "userTrigger", "wait=", "help"])
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
  GPIO.setup(inputChannel, GPIO.IN)
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
  # Use the global fileNames list
  global fileNames

  fileName = random.choice(fileNames)
  startFile(fileName)

# ==============================================================================
# Wait for the playing music to finish
# ------------------------------------------------------------------------------
def waitForCurrentFile():
  while mixer.music.get_busy():
    # Sleep for a second
    time.sleep(1)
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
    while True:
      while GPIO.input(inputChannel):
        logging.debug("Input channel high")
      while not GPIO.input(inputChannel)
        logging.debug("Input channel low")
    GPIO.wait_for_edge(inputChannel, GPIO.RISING)
    logging.info("Motion detected")

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