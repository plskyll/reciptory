from django.db import models
from django.contrib.auth.models import User




class Recipe(models.Model):
    CUISINE_CHOICES = [
        ('ukrainian', 'Українська'),
        ('italian', 'Італійська'),
        ('french', 'Французька'),
        ('indian', 'Індійська'),
        ('chinese', 'Китайська'),
        ('japanese', 'Японська'),
        ('american', 'Американська'),
        ('mexican', 'Мексиканська'),
        ('thai', 'Тайська'),
        ('other', 'Інша'),
    ]

    title = models.CharField(max_length=200, verbose_name="Назва")
    ingredients = models.TextField(verbose_name="Інгредієнти")
    instructions = models.TextField(verbose_name="Інструкції")
    cooking_time = models.PositiveIntegerField(verbose_name="Час приготування (хв)")
    cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES, default='ukrainian', verbose_name="Кухня")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    image = models.ImageField(upload_to='recipes/', null=True, blank=True, verbose_name="Зображення")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепти"
        ordering = ['-created_at']


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', verbose_name="Рецепт")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="Автор")
    text = models.TextField(verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f'Коментар від {self.author.username} до {self.recipe.title}'

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        ordering = ['-created_at']


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="Користувач")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Рецепт")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Додано")

    class Meta:
        verbose_name = "Улюблений рецепт"
        verbose_name_plural = "Улюблені рецепти"
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'