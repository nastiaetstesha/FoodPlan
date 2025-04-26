from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.decorators import login_required


from .models import User
from .models import Recipe, Ingredient, UserPage

# UserRecipeFeedback


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
    recipes = Recipe.objects.filter(on_index=True)
    return render(request, "index.html", {"recipes": recipes})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                user_obj = get_object_or_404(User, email=email)
            except Http404:
                return HttpResponse("Пользователь не найден")
            user = authenticate(username=user_obj.username, password=password)
            print(user)
            if user:
                login(request, user)
                return redirect("lk")
            else:
                return HttpResponse("Неправильный e-mail или пароль")
        # Закомментил код Насти чтобы можно было быстро откатить
        """
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        print(f"Ввод: email={email}, password={password}")
        try:
            user_obj = User.objects.get(email=email)
            print(f"Нашли пользователя: {user_obj}")
            print(f'{user_obj.email}')
            print(f'{user_obj.password}')
            print(f'{user_obj.is_active}')
            user = authenticate(request, email=email, password=password)
            print(f"Результат аутентификации: {user}")
            if user:
                login(request, user)
                print("Успешный вход, редирект в lk")
                return redirect("lk")
            else:
                print("Неверный пароль")
        except User.DoesNotExist:
            print("Пользователь не найден")
            """
    return render(request, "auth.html")


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.all().prefetch_related("ingredients"), pk=recipe_id
    )
    ingredients = recipe.ingredients.all()
    caloricity = int(recipe.get_calories())
    price = int(recipe.get_price())
    return render(
        request,
        "recipe_card.html",
        {
            "recipe": recipe,
            "ingredients": ingredients,
            "caloricity": caloricity,
            "price": price,
        },
    )


@login_required
def recipe_feedback(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = get_object_or_404(UserPage, user=request.user)
        liked = request.POST.get("liked") is True
        disliked = request.POST.get("disliked") is True
        if liked:
            user.add_to_liked(recipe)
        elif disliked:
            user.add_to_disliked(recipe)
        return redirect("recipe_detail", recipe_id=recipe_id)
    except Http404:
        return redirect("login")


def shopping_list(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredients.all()

    total_price = sum(item.ingredient.price * item.mass / 100 for item in ingredients)

    context = {
        "recipe": recipe,
        "ingredients": ingredients,
        "total_price": total_price,
    }
    return render(request, "shopping_list.html", context)


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    return render(request, 'lk.html', {'user': request.user})


def lk(request):
    context = {}
    return render(request, "lk.html", context)


def order(request):
    context = {}
    return render(request, "order.html", context)
