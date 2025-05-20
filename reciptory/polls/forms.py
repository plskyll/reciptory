from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Recipe, Comment

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Неправильне ім'я користувача або пароль")
            if not user.is_active:
                raise forms.ValidationError("Цей обліковий запис неактивний")

        return cleaned_data

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'ingredients', 'instructions', 'cooking_time', 'cuisine', 'image']
        widgets = {
            'ingredients': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введіть інгредієнти, кожен з нового рядка'}),
            'instructions': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Опишіть процес приготування'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишіть ваш коментар'}),
        }

class RecipeSearchForm(forms.Form):
    cuisine = forms.ChoiceField(
        choices=[('', 'Всі кухні')] + Recipe.CUISINE_CHOICES,
        required=False,
        label='Кухня'
    )
    query = forms.CharField(
        required=False,
        label='Пошук',
        widget=forms.TextInput(attrs={'placeholder': 'Пошук за назвою або інгредієнтами'})
    )