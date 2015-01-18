# Uses a motion sensor to trigger sound files

# ==============================================================================
# Imports
# ------------------------------------------------------------------------------
import motionSensor
import soundPlayer
import logging
import sys
import getopt
import glob
import random
import ConfigParser
import datetime
import time

# ==============================================================================
# Globals
# ------------------------------------------------------------------------------
gDebugMode = False
gUserTrigger = False
gLogName = "motionSound"
gLogFile = "motionSound.log"
gConfigFile = "motionSound.cfg"
gLogger = logging.getLogger(gLogName)

# ==============================================================================
# parseArgs
# Parse the command line arguments
# ------------------------------------------------------------------------------
def parseArgs():
  global gDebugMode
  global gUserTrigger

  try:
    # Get the list of options provided, and there args
    opts, args = getopt.getopt(sys.argv[1:], "du",["debug", "userTrigger"])
  except getopt.GetoptError as e:
    print("Error parsing args: %s" % (e))
    sys.exit(0)

  # Loop through and react to each option
  for opt, arg in opts:
    if opt in ("-d", "--debug"):
      gDebugMode = True
    elif opt in ("-u", "--userTrigger"):
      gUserTrigger = True

# ==============================================================================
# init
# Initialise self and all sub systems
# ------------------------------------------------------------------------------
def init():
  global gLogger

  parseArgs()

  # Initialise console logger
  consoleHandle = logging.StreamHandler()
  lvl = logging.INFO
  if gDebugMode:
    lvl = logging.DEBUG
  formatString = "%(levelname)-8s %(asctime)s %(funcName)s:%(lineno)s: %(message)s"
  formatter = logging.Formatter(formatString)
  consoleHandle.setLevel(lvl)
  consoleHandle.setFormatter(formatter)
  gLogger.setLevel(lvl)
  gLogger.addHandler(consoleHandle)
  

  # Initialise the file logging
  fileHandle = logging.FileHandler(gLogFile)
  fileHandle.setLevel(logging.INFO)
  fileHandle.setFormatter(formatter)
  gLogger.addHandler(fileHandle)

  gLogger.debug("Initialising")

  config = readConfig()
  inputChannel = config.getint("gpio", "inputpin")
  if gUserTrigger:
    inputChannel = -1

  motionSensor.init(inputPin=inputChannel, logName=gLogName)
  soundPlayer.init(logName=gLogName)

# ==============================================================================
# cleanup
# Perform any necessary cleanup before exitting
# ------------------------------------------------------------------------------
def cleanup():
  gLogger.debug("Cleaning up")
  motionSensor.cleanup()

# ==============================================================================
# readConfig
# Read the config file
# ------------------------------------------------------------------------------
def readConfig():
  config = ConfigParser.RawConfigParser()
  config.read(gConfigFile)
  return config

# ==============================================================================
# writeConfig
# Write a given config to the file
# ------------------------------------------------------------------------------
def writeConfig(config):
  with open(gConfigFile, "wb") as configfile:
    config.write(configfile)

# ==============================================================================
# playRandomFile
# Choose a random file from our directory and play it
# ------------------------------------------------------------------------------
def playRandomFile():
  config = readConfig()

  # Build a list of ogg files in this directory
  filenames = glob.glob("*.ogg")
  # Choose a random file from this list
  gLogger.debug("Choosing random file")
  filename = random.choice(filenames)

  # Make sure this file isn't in the list of recently played files
  recentlyPlayedStr = config.get("recentlyplayed", "list")
  recentlyPlayed = recentlyPlayedStr.split("/")
  if len(recentlyPlayed) < len(filenames):
    while filename in recentlyPlayed:
      gLogger.debug("%s has been played recently, choosing another file" % (filename))
      filename = random.choice(filenames)

  # Add this file to the list of recently played ones
  recentlyPlayed.append(filename)
  # Only keep up to a max number of recently played files
  maxListLength = config.getint("recentlyplayed", "maxlistlength")
  recentlyPlayed = recentlyPlayed[-maxListLength:]

  # Write the updated list back to the config file
  recentlyPlayedStr = "/".join(recentlyPlayed)
  config.set("recentlyplayed", "list", recentlyPlayedStr)
  writeConfig(config)

  # Play this file
  soundTimeout = config.getint("timeouts", "soundtimeout")
  soundPlayer.play(filename, timeout=soundTimeout)

# ==============================================================================
# shouldPlaySound
# Decides whether a file should be played
# ------------------------------------------------------------------------------
def shouldPlaySound():
  shouldPlay = True

  config = readConfig()

  # Sound can be completely disabled, if it is just exit the method here
  if config.getboolean("misc", "sounddisabled"):
    gLogger.info("Sound is disabled in the config file")
    return False

  # Don't allow sound before or after certain times
  # Exit the method if either of these checks fail
  currentTime = datetime.datetime.now()
  if currentTime.hour < config.getint("allowedtimes", "earliest"):
    gLogger.info("Too early to play sound")
    return False
  if currentTime.hour >= config.getint("allowedtimes", "latest"):
    gLogger.info("Too late to play sound")
    return False

  # Only play a sound a certain percentage of the time
  currentChance = config.getint("chance", "current")
  generatedNum = random.randint(1, 100)
  if generatedNum > currentChance:
    gLogger.debug("Generated %d, must be %d or lower" % (generatedNum, currentChance))
    # Increment the chance to play
    incr = config.getint("chance", "increment")
    currentChance = currentChance + incr
    maxChance = config.getint("chance", "max")
    currentChance = min(currentChance, maxChance)
    gLogger.info("Chance to play is now %d%%" % (currentChance))
    shouldPlay =  False
  else:
    # Reset the chance to play
    initial = config.getint("chance", "initial")
    currentChance = initial

  # Write the new current chance to config
  config.set("chance", "current", currentChance)

  writeConfig(config)

  return shouldPlay

# ==============================================================================
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  init()

  # Catch keyboard interrupts
  try:
    while True:
      motionSensor.waitForMotion()

      if shouldPlaySound():
        playRandomFile()

        config = readConfig()
        secondsToWait = config.getint("timeouts", "secondstowaitaftersound")
        gLogger.debug("Waiting %d seconds" % (secondsToWait))
        time.sleep(secondsToWait)
  except KeyboardInterrupt:
    gLogger.debug("Keyboard interrupt caught")
    cleanup()
