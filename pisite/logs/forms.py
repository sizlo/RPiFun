from django import forms
from logs.models import Log

class LineCountForm(forms.Form):
  linesToFetch = forms.IntegerField(label="Number of lines to show", min_value=0, initial=Log.defaultLinesToShow)