from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import Question
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import UserLoginForm


# Create your views here.
def home_view(request):
    return render(request, 'home.html')

@login_required
def question_list(request):
    objects = Question.objects.all()
    context = {'questions': objects}
    return render(request, 'question_list.html', context)


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:question_list')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
