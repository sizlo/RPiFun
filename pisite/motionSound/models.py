from django.db import models
from django.conf import settings

# Create your models here.
class TextFile(models.Model):
  name = models.CharField(max_length=50)
  filePath = models.CharField(max_length=300)
  defaultLinesToShow=100
  
  def getFileContents(self):
    txtFile = open(settings.BASE_DIR + "/" + self.filePath)
    contents = txtFile.read()
    txtFile.close()
    return contents

  def getLastNLines(self, n=defaultLinesToShow):
    txtFile = open(settings.BASE_DIR + "/" + self.filePath)
    lines = txtFile.readlines()
    txtFile.close()

    lastNLines = "".join(lines[-n:])
    return lastNLines

  def __unicode__(self):
    return self.name