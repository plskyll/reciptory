from django.db import models

# Create your models here.
class Question(models.Model):
  question_text = models.CharField(max_length=255)
  pub_date = models.DateTimeField(auto_now_add=True)

class Choice(models.Model):
  question  = models.CharField(max_length=255)
  choice_text = models.TextField()
  votes = models.IntegerField(default=0)