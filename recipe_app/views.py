from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

from .models import User
from .models import Recipe, UserRecipeFeedback


def registration(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("lk")  # после регистрации — на личный кабинет
    else:
        form = CustomUserCreationForm()
    return render(request, "registration.html", {"form": form})


def index(request):
    recipes = Recipe.objects.all()  # Все рецепты для главной
    return render(request, "index.html", {"recipes": recipes})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        print(f"Ввод: email={email}, password={password}")
        try:
            user_obj = User.objects.get(email=email)
            print(f"Нашли пользователя: {user_obj}")
            user = authenticate(request, username=user_obj.username, password=password)
            print(f"Результат аутентификации: {user}")
            if user:
                login(request, user)
                print("Успешный вход, редирект в lk")
                return redirect("lk")
            else:
                print("Неверный пароль")
        except User.DoesNotExist:
            print("Пользователь не найден")
    return render(request, "auth.html")


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, "recipe_detail.html", {"recipe": recipe})


@login_required
def recipe_feedback(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    liked = request.POST.get("liked") == "true"

    feedback, created = UserRecipeFeedback.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={'liked': liked}
    )
    return redirect('recipe_detail', recipe_id=recipe_id)


def shopping_list(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredients.all()

    total_price = sum(
        item.ingredient.price * item.mass / 100
        for item in ingredients
    )

    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'total_price': total_price,
    }
    return render(request, 'shopping_list.html', context)


def user_logout(request):
    logout(request)
    return redirect("login")


def card1(request):
    context = {}
    return render(request, "card1.html", context)


def card2(request):
    context = {}
    return render(request, "card2.html", context)


def card3(request):
    context = {}
    return render(request, "card3.html", context)


def lk(request):
    context = {}
    return render(request, "lk.html", context)


def order(request):
    context = {}
    return render(request, "order.html", context)

