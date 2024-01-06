# forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import UserProfile, RoommatePreferences, PetChoice, Pet, Interest
from django.core import validators


class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(required=True, validators=[validators.EmailValidator(message="Invalid Email")], widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2','is_active')



class UserProfileForm(forms.ModelForm):
    city = forms.ChoiceField(choices=UserProfile.CITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date of Birth'}))
    occupation = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}))
    sex = forms.ChoiceField(choices=UserProfile.SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    education = forms.ChoiceField(choices=UserProfile.EDUCATION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    move_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Move-in Date'}))
    about = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'About'}))
    


    class Meta:
        model = UserProfile
        fields = ['dob', 'city', 'occupation', 'sex', 'education', 'move_in_date', 'about', 'profile_picture']

class RoommatePreferencesForm(forms.ModelForm):
    sleep_hours = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sleep Hours'}))
    drinks = forms.ChoiceField(choices=RoommatePreferences.THREE_OPTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    drugs = forms.ChoiceField(choices=RoommatePreferences.THREE_OPTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    smoke = forms.ChoiceField(choices=RoommatePreferences.THREE_OPTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    loud_music = forms.ChoiceField(choices=RoommatePreferences.THREE_OPTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    rooms = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Rooms'}))
    budget = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget'}))
    meals = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Meals'}))

    class Meta:
        model = RoommatePreferences
        fields = ['sleep_hours', 'drinks', 'drugs', 'smoke', 'loud_music', 'rooms', 'budget', 'meals']


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['pets']
        widgets = {
            'pets': forms.CheckboxSelectMultiple,
            'class': 'form-control'
        }

		
class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['interests']
        widgets = {
            'interests': forms.CheckboxSelectMultiple,
            'class': 'form-control'
        }


class RoommateSearchForm(forms.Form):
    keyword = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'keyword'}))
    city = forms.ChoiceField(choices=UserProfile.CITY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control','placeholder': 'city'}))
    gender = forms.ChoiceField(choices=UserProfile.SEX_CHOICES,required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    age_min = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'min. age'}))
    age_max = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'max. age'}))



# class WidgetForm(forms.ModelForm):
#     features = forms.ModelMultipleChoiceField(
#         queryset=Feature.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#     class Meta:
#         model = Widget