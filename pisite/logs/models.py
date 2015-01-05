from django.db import models
from django.conf import settings

# Create your models here.
class Log(models.Model):
  name = models.CharField(max_length=50)
  filePath = models.CharField(max_length=300)
  defaultLinesToShow=100
  
  def getFileContents(self):
    logFile = open(settings.BASE_DIR + "/" + self.filePath)
    contents = logFile.read()
    logFile.close()
    return contents

  def getLastNLines(self, n=defaultLinesToShow):
    logFile = open(settings.BASE_DIR + "/" + self.filePath)
    lines = logFile.readlines()
    logFile.close()

    lastNLines = "".join(lines[-n:])
    return lastNLines

  def __unicode__(self):
    return self.name