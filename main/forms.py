from django import forms

from .models import Memory


class AddMemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ("place", "description")
        labels = {
            "place": "",
            "description": "",
        }
        widgets = {
            "place": forms.TextInput(
                attrs={
                    "class": "form-place",
                    "placeholder": "Место",
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-description",
                    "autocomplete": "off",
                }
            ),
        }
