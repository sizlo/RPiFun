from django import forms

class UploadSoundForm(forms.Form):
    sound = forms.FileField()
    startTime = forms.CharField(label="Start time as HH:MM:SS.mmm", max_length=12, initial="00:00:00.000")
    duration = forms.CharField(label="Duration as HH:MM:SS.mmm", max_length=12, initial="00:00:15.000")