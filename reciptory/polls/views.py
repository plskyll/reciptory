from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm
from .models import Question


# Create your views here.
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
