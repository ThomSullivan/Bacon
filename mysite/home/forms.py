from django import forms
from captcha.fields import ReCaptchaField


class contactMeForm(forms.Form):
    name = forms.CharField(max_length=50)
    emailAddress = forms.EmailField(max_length=100)
    message = forms.CharField(label="Message", widget=forms.Textarea())
    captcha = ReCaptchaField()
    