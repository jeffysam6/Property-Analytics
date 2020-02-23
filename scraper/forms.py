from django import forms


class LocationForm(forms.ModelForm):

    class Meta:
        fields = ('location',)