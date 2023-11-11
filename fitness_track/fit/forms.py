from django import forms
from django.forms import DateInput
from django.utils import timezone
from django.core.validators import RegexValidator
from fit.models import Food
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'type':'password'}))

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Password',
                                                              'type': 'password'}))
    password2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'
                                                              , 'type': 'password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class WeightLogForm(forms.Form):
    weight = forms.CharField(label='Log New Weight', max_length=5)

class NewFoodForm(forms.Form):
    date = forms.DateField(widget=DateInput, initial=timezone.now)
    description = forms.CharField(label="Description", max_length=30, validators=[RegexValidator('^[\w .,()+-]+$', message='Description must be alphanumeric', code='invalid_desc')])
    calories = forms.IntegerField(label="Calories")

class ExistFoodForm(forms.Form):
    date = forms.DateField(widget=DateInput, initial=timezone.now)
    description = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ExistFoodForm, self).__init__(*args, **kwargs)
        self.fields['description'].choices = Food.objects.filter(user=self.request.user).order_by('description').values_list("description", "description").distinct()

class DateInput(forms.DateInput):
    input_type = 'date'
