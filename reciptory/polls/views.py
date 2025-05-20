from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserLoginForm, RecipeForm, CommentForm, RecipeSearchForm
from .models import Recipe, Comment, Favorite
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
# Home view
def home_view(request):
    # Отримуємо останні 6 рецептів для відображення на головній сторінці
    latest_recipes = Recipe.objects.all().order_by('-created_at')[:6]
    return render(request, 'home.html', {'latest_recipes': latest_recipes})


# Authentication views
def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Реєстрація успішна! Ласкаво просимо!")
            return redirect('polls:home')
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

                # Обробка чекбокса remember_me
                remember_me = request.POST.get('remember_me')
                if not remember_me:
                    # Сесія завершується після закриття браузера
                    request.session.set_expiry(0)
                else:
                    # Сесія триває стандартний час (напр., 30 днів)
                    request.session.set_expiry(None)

                messages.success(request, f"Вітаємо, {username}!")
                return redirect('polls:home')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Ви вийшли з системи.")
    return redirect('polls:home')


# Recipe views
def recipe_list(request):
    cuisines = [{'id': choice[0], 'name': choice[1]} for choice in Recipe.CUISINE_CHOICES]

    form = RecipeSearchForm(request.GET)
    recipes = Recipe.objects.all()

    if form.is_valid():
        cuisine = form.cleaned_data.get('cuisine')
        query = form.cleaned_data.get('query')

        if cuisine:
            recipes = recipes.filter(cuisine=cuisine)

        if query:
            recipes = recipes.filter(
                Q(title__icontains=query) |
                Q(ingredients__icontains=query)
            )

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Recipe.objects.filter(favorited_by__user=request.user)

    context = {
        'form': form,
        'recipes': recipes,
        'cuisines': cuisines,  # передаємо сформований список кухонь
        'user_favorites': user_favorites,
    }

    return render(request, 'recipe_list.html', context)

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    comments = recipe.comments.all()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.recipe = recipe
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Коментар додано успішно!")
            return redirect('polls:recipe_detail', recipe_id=recipe.id)
    else:
        comment_form = CommentForm()

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'is_favorite': is_favorite,
        'comment_form': comment_form,
    })


@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        print("POST data:", request.POST)  # Для діагностики
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            messages.success(request, "Рецепт успішно створено!")
            return redirect('polls:recipe_detail', recipe_id=recipe.id)
        else:
            print("Form errors:", form.errors)  # Щоб побачити помилки
    else:
        form = RecipeForm()

    return render(request, 'recipe_form.html', {'form': form, 'form_type': 'create'})


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Перевірка чи поточний користувач є автором рецепту
    if recipe.author != request.user:
        messages.error(request, "Ви не маєте права редагувати цей рецепт.")
        return redirect('polls:recipe_detail', recipe_id=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, "Рецепт успішно оновлено!")
            return redirect('polls:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipe_form.html', {
        'form': form,
        'recipe': recipe,
        'form_type': 'edit'
    })


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.author != request.user:
        messages.error(request, "Ви не маєте права видаляти цей рецепт.")
        return redirect('polls:recipe_detail', recipe_id=recipe_id)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Рецепт успішно видалено!")
        return redirect('polls:user_recipes')

    return render(request, 'recipe_confirm_delete.html', {'recipe': recipe})


# Favorite views
@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        favorite.delete()
        is_favorite = False
        message = "Рецепт видалено з обраного."
    else:
        is_favorite = True
        message = "Рецепт додано до обраного."

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite,
            'message': message,
        })

    messages.success(request, message)
    return redirect('polls:recipe_detail', recipe_id=recipe_id)


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    recipes = [fav.recipe for fav in favorites]
    return render(request, 'favorite_list.html', {'favorites': recipes})


# Filtered views
def recipes_by_cuisine(request, cuisine):
    recipes = Recipe.objects.filter(cuisine=cuisine)
    return render(request, 'recipe_list.html', {
        'recipes': recipes,
        'cuisine': dict(Recipe.CUISINE_CHOICES).get(cuisine),
        'form': RecipeSearchForm(initial={'cuisine': cuisine})
    })


@login_required
def user_recipes(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request, 'user_recipes.html', {'recipes': recipes})

def terms_view(request):
    return render(request, 'terms.html')

def privacy_view(request):
    return render(request, 'privacy.html')

@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        messages.error(request, "Ви не маєте права редагувати цей коментар.")
        return redirect('polls:recipe_detail', recipe_id=comment.recipe.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Коментар успішно оновлено.")
            return redirect('polls:recipe_detail', recipe_id=comment.recipe.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comment_edit.html', {'form': form, 'comment': comment})

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        messages.error(request, "Ви не маєте права видаляти цей коментар.")
        return redirect('polls:recipe_detail', recipe_id=comment.recipe.id)

    if request.method == 'POST':
        recipe_id = comment.recipe.id
        comment.delete()
        messages.success(request, "Коментар видалено.")
        return redirect('polls:recipe_detail', recipe_id=recipe_id)

    return render(request, 'comment_delete_confirm.html', {'comment': comment})

@staff_member_required
def admin_recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'admin_recipe_list.html', {'recipes': recipes})

@staff_member_required
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'admin_user_list.html', {'users': users})

@staff_member_required
def admin_comment_list(request):
    comments = Comment.objects.all()
    return render(request, 'admin_comment_list.html', {'comments': comments})

@staff_member_required
def admin_change_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Пароль для користувача {user.username} успішно змінено.")
            update_session_auth_hash(request, user)  # щоб не вийшов адміністратор із системи
            return redirect('polls:admin_user_list')
    else:
        form = AdminPasswordChangeForm(user)
    return render(request, 'admin_change_password.html', {'form': form, 'user_obj': user})

@staff_member_required
def admin_change_password(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 and new_password1 == new_password2:
            user_obj.set_password(new_password1)
            user_obj.save()
            messages.success(request, 'Пароль успішно змінено.')
            return redirect('polls:admin_user_list')  # Перенаправлення до списку користувачів
        else:
            messages.error(request, 'Паролі не співпадають або не можуть бути порожніми.')

    return render(request, 'admin_change_password.html', {'user_obj': user_obj})

@staff_member_required
def admin_comment_delete(request, comment_id):
    # Шукаємо коментар за ID або повертаємо 404, якщо не знайдемо
    comment = get_object_or_404(Comment, id=comment_id)

    # Можна додати перевірку, чи користувач має права видаляти коментарі (опціонально)
    # наприклад, якщо є група "admin" або is_staff
    if not request.user.is_staff:
        # Якщо не адміністратор, можна показати помилку або редірект
        return redirect('polls:admin_comment_list')

    # Видаляємо коментар
    comment.delete()

    # Переадресація назад на список коментарів
    return redirect('polls:admin_comment_list')