from django import forms
from django_training.app_demo.models import Course


class CourseForm(forms.ModelForm):
    """Form for creating and updating Course instances."""

    class Meta:
        model = Course
        fields = ["title", "code", "description", "instructor", "credits", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Introduction to Python"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. CS-101"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Course curriculum details..."},
            ),
            "instructor": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Prof. Alan Turing"}),
            "credits": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 10}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
