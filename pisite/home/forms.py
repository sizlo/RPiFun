from django import forms

class UploadSoundForm(forms.Form):
    sound = forms.FileField()