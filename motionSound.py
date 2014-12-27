# Uses a motion sensor on the GPIO and plays a random ogg file from a selection
# when active

# ==============================================================================
# Imports
# ------------------------------------------------------------------------------
from pygame import mixer
import time
import sys
import getopt

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
# Log a debug message
# ------------------------------------------------------------------------------
def debugLog(msg):
  # We want to use the global debugMode
  global debugMode

  if debugMode:
    print msg

# ==============================================================================
# Initialise the program
# ------------------------------------------------------------------------------
def init():
  parseArgs()
  debugLog("Initialising")
  # Initialise the mixer
  mixer.init()

# ==============================================================================
# Start playing a sound file
# ------------------------------------------------------------------------------
def startFile(theFileName):
  debugLog("Playing " + theFileName)
  mixer.music.load(theFileName)
  mixer.music.play()

# ==============================================================================
# Wait for the playing music to finish
# ------------------------------------------------------------------------------
def waitForCurrentFile():
  while mixer.music.get_busy():
    # Sleep for a second
    time.sleep(1)
  debugLog("Music finished")


# ==============================================================================
# Program entry / main
# ------------------------------------------------------------------------------
init()
startFile('cenashort.ogg')
waitForCurrentFile()