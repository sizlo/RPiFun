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

# ==============================================================================
# Global variables
# ------------------------------------------------------------------------------
debugMode = False

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
  # We want to use the global debugMode
  global debugMode

  try:
    # Get the list of options provided, and there args
    opts, args = getopt.getopt(sys.argv[1:], "d",["debug"])
  except getopt.GetoptError:
    # Print usage and exit on unknown option
    exitWithMessage("Usage: " + sys.argv[0] + " [-d|--debug]")

  # Loop through and react to each option
  for opt, arg in opts:
    if opt in ("-d", "--debug"):
      debugMode = True

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

  # Initialise the mixer
  mixer.init()

# ==============================================================================
# Start playing a sound file
# ------------------------------------------------------------------------------
def startFile(theFileName):
  logging.info("Playing %s", theFileName)
  mixer.music.load(theFileName)
  mixer.music.play()

# ==============================================================================
# Wait for the playing music to finish
# ------------------------------------------------------------------------------
def waitForCurrentFile():
  while mixer.music.get_busy():
    # Sleep for a second
    time.sleep(1)
  logging.info("Music finished")


# ==============================================================================
# Program entry / main
# ------------------------------------------------------------------------------
init()
startFile('cenashort.ogg')
waitForCurrentFile()