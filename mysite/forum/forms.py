from django import forms
from django.core.exceptions import ValidationError
from django.core import validators

# strip means to remove whitespace from the beginning and the end before storing the column
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Leave a comment'}),label='',
        required=True, max_length=500, min_length=3, strip=True)