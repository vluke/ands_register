from django import forms
from django.forms.widgets import Textarea

from .publishing import PUBLIC, MEDIATED, PRIVATE, UNPUBLISHED

ACCESS_TYPE_CHOICES = (
    (PUBLIC, 'Public'),
    (MEDIATED, 'Mediated'),
    (PRIVATE, 'Private'),
    (UNPUBLISHED, 'Unpublished'),
)

NO_LICENCE_TYPE_CHOICES = [x for x in ACCESS_TYPE_CHOICES if x[0] is not PUBLIC]

class PublishingForm(forms.Form):
    custom_description = forms.CharField(required=False, widget=Textarea)
    custom_authors = forms.CharField(required=False)

    def __init__(self, has_license, *args, **kwargs):
        super(PublishingForm, self).__init__(*args, **kwargs)
        if has_license:
            self.fields['access_type'] = forms.ChoiceField(ACCESS_TYPE_CHOICES, initial=UNPUBLISHED)
        else:
            self.fields['access_type'] = forms.ChoiceField(NO_LICENCE_TYPE_CHOICES, initial=UNPUBLISHED)
