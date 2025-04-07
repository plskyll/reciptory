from django.shortcuts import render
from .models import Question

# Create your views here.

def question_list(request):
    objects = Question.objects.all()
    context = {"questions": objects}
    return render(request, 'question_list.html', context)