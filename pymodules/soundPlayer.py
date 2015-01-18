# Plays sound files using pygame

# ==============================================================================
# Imports
# ------------------------------------------------------------------------------
import pygame
import time
import logging

# ==============================================================================
# Globals
# ------------------------------------------------------------------------------
gLogger = logging.getLogger()

# ==============================================================================
# init
# ------------------------------------------------------------------------------
def init(logName=""):
  global gLogger

  gLogger = logging.getLogger(logName)

  pygame.mixer.init()

# ==============================================================================
# startFile
# Starts playing a given filename
# ------------------------------------------------------------------------------
def startFile(filename):
  # Make sure we catch any errors from pygame
  try:
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    gLogger.info("Playing %s" % (filename))
  except pygame.error:
    gLogger.error("Error playing file %s: %s" % (filename, pygame.get_error()))

# ==============================================================================
# waitForCurrentFile
# Wait for the current playing sound to finish or stops it after a timeout
# ------------------------------------------------------------------------------
def waitForCurrentFile(timeout):
  # Ensure we cut off playback after a timeout
  startTime = time.time()
  cutoffTime = startTime + timeout
  while pygame.mixer.music.get_busy():
    # Sleep for a second
    time.sleep(1)
    # If it's been 15s stop playback
    currentTime = time.time()
    if currentTime > cutoffTime:
      pygame.mixer.music.stop()
      gLogger.info("Sound cut off after %s seconds" % (timeout))

  gLogger.debug("Sound finished")

# ==============================================================================
# play
# Play and wait for a given file
# ------------------------------------------------------------------------------
def play(filename, timeout=15):
  startFile(filename)
  waitForCurrentFile(timeout)

