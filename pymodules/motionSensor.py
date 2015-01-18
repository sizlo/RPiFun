# Initialises RPi GPIO for motion sensor and provides methods to listen to it

gUserTrigger = False

# ==============================================================================
# Imports
# ------------------------------------------------------------------------------
import time
import logging
# Try to import the RPi GPIO stuff
# If it fails activate a user trigger mode
try:
  import RPi.GPIO as GPIO
except ImportError as e:
  print("Rpi.GPIO doesn't exist, running in user trigger mode")
  gUserTrigger = True
except RuntimeError as e:
  print("Error importing GPIO. Are you running under sudo?")

# ==============================================================================
# Globals
# ------------------------------------------------------------------------------
gInputPin = -1
gLogger = logging.getLogger()

# ==============================================================================
# init
# Initialise the GPIO pins
# ------------------------------------------------------------------------------
def init(inputPin=-1, logName=""):
  global gUserTrigger
  global gInputPin
  global gLogger

  gLogger = logging.getLogger(logName)

  # If no input pin was supplied activate user trigger mode
  if inputPin == -1:
    gUserTrigger = True

  # If we're not in user trigger mode set up the pins
  if not gUserTrigger:
    # Set up the pin numbering mode
    GPIO.setmode(GPIO.BOARD)

    # Set up the input pin
    gInputPin = inputPin
    GPIO.setup(gInputPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    gLogger.debug("Set pin %d as motion sensor input" % (gInputPin))

# ==============================================================================
# waitForMotion
# Wait for the motion sensor pin to go high
# ------------------------------------------------------------------------------
def waitForMotion():
  gLogger.info("Waiting for motion")

  # In user trigger mode just ask for input
  if gUserTrigger:
    raw_input("Press enter to trigger")
    gLogger.info("Triggered by user input")
  else:
    # Add an event detect for the edge we want
    GPIO.add_event_detect(gInputPin, GPIO.RISING)
    # Wait for that event
    while not GPIO.event_detected(gInputPin):
      time.sleep(1)
    # Remove the event detect
    GPIO.remove_event_detect(gInputPin)
    gLogger.info("Motion detected")

# ==============================================================================
# cleanup
# Cleans up the GPIO state
# ------------------------------------------------------------------------------
def cleanup():
  if not gUserTrigger:
    GPIO.cleanup()


# ==============================================================================
# main
# Called if executed as script
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG, format="%(message)s")
  
  # Setup with pin 7
  init(inputPin=7)

  # And continuously print when motion is detected
  try:
    while True:
      waitForMotion()
  except KeyboardInterrupt:
    gLogger.debug("Keyboard interrupt caught")
    cleanup()