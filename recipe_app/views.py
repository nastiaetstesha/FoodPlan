from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from random import choice

from .forms import (
    CustomUserCreationForm,
    LoginForm,
    CustomPasswordChangeForm,
    OrderForm,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging
from django.db import transaction
from django.core.validators import validate_email


from .models import (
    User,
    Recipe,
    Ingredient,
    UserPage,
    DailyMenu,
    UserPage,
    MenuType,
    Subscription,
    FoodTag,
)


logger = logging.getLogger(__name__)


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
    if Recipe.objects.exists():
        recipes = Recipe.objects.filter(on_index=True)
    else:
        recipes = []
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
    userpage = None
    if request.user.is_authenticated:
        userpage = UserPage.objects.filter(user=request.user).first()
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
            "user_page": userpage,
        },
    )


@login_required
def recipe_feedback(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user_page = get_object_or_404(UserPage, user=request.user)

    if 'disliked' in request.POST:
        # При первом нажатии установить счетчик
        if 'replace_attempts' not in request.session:
            request.session['replace_attempts'] = 2

        # Проверить, сколько осталось попыток
        if request.session['replace_attempts'] > 0:
            # Добавляем рецепт в дизлайкнутые
            user_page.disliked_recipes.add(recipe)

            # Находим другой случайный рецепт
            disliked_ids = user_page.disliked_recipes.values_list('id', flat=True)
            new_recipe = Recipe.objects.exclude(id__in=disliked_ids).order_by('?').first()

            # Уменьшаем количество оставшихся замен
            request.session['replace_attempts'] -= 1

            if new_recipe:
                return redirect('recipe_detail', recipe_id=new_recipe.id)
            else:
                # Если новых рецептов нет, вернуть назад
                return redirect('recipe_detail', recipe_id=recipe_id)

        else:
            # Нет попыток замены — просто дизлайкнуть
            user_page.disliked_recipes.add(recipe)
            messages.info(request, "Вы использовали все попытки сменить блюдо.")
            return redirect('recipe_detail', recipe_id=recipe_id)

    elif 'liked' in request.POST:
        # Очистить попытки, если поставили лайк
        request.session.pop('replace_attempts', None)

        # Добавляем лайк
        if recipe in user_page.disliked_recipes.all():
            user_page.disliked_recipes.remove(recipe)
        user_page.liked_recipes.add(recipe)

        return redirect('recipe_detail', recipe_id=recipe_id)

    return redirect('recipe_detail', recipe_id=recipe_id)


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
    return render(request, "lk.html", {"user": request.user})


def lk_view(request):
    user_page, created = UserPage.objects.get_or_create(
        user=request.user,
        defaults={
            "username": request.user.username,
        },
    )

    if not user_page.username:
        user_page.username = request.user.username
        user_page.save(update_fields=["username"])

    is_subscribed = user_page.is_subscribed
    menu_type = user_page.menu_type
    avatar = user_page.image
    allergies = user_page.allergies.all()
    persons_count = 1
    if is_subscribed and menu_type:
        today_menu = user_page.menu_type.dailymenus.first()
        recipes = [today_menu.breakfast, today_menu.lunch, today_menu.dinner]
        persons_count = user_page.subscription.get().persons

    else:
        random_recipe = Recipe.objects.order_by("?").first()
        recipes = [random_recipe]

    # Получаем инфу для персонального меню
    allergies_info = (
        ", ".join([allergy.name for allergy in allergies]) if allergies else "нет"
    )
    calories = sum(
        recipe.calories for recipe in recipes if recipe
    )  # Считаем сумму калорий блюд
    meals_count = len(recipes)

    context = {
        "recipes": recipes,
        "user_page": user_page,
        "persons_count": persons_count,
        "allergies_info": allergies_info,
        "calories": int(calories),
        "meals_count": meals_count,
        "avatar": avatar,
        "menu_type": menu_type,
        "is_subscribed": is_subscribed,
    }
    return render(request, "lk.html", context)


@login_required
def upload_avatar(request):
    user_page = UserPage.objects.filter(user=request.user).first()

    if request.method == "POST":
        if "image" not in request.FILES:
            messages.error(request, "Файл не был загружен")
            return redirect("lk")

        user_page.image = request.FILES["image"]
        user_page.save()
        messages.success(request, "Аватар успешно обновлён")
        return redirect("lk")

    return redirect("lk")


@login_required
def profile_update(request):
    if request.method == "POST":
        try:
            user = request.user
            user_page = UserPage.objects.filter(user=request.user).first()

            old_email = user.email
            old_username = user_page.username if hasattr(user_page, "username") else ""

            new_username = request.POST.get("username", old_username)
            new_email = request.POST.get("email", old_email).lower().strip()

            if (
                new_email != old_email
                and User.objects.filter(email=new_email).exclude(pk=user.pk).exists()
            ):
                raise ValueError("Этот email уже используется другим пользователем")

            user_page.username = new_username
            user.email = new_email

            with transaction.atomic():
                user.save()
                user_page.save()

            messages.success(request, "Данные успешно обновлены")

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            messages.error(request, "Произошла ошибка при обновлении данных")

            if "user" in locals():
                user.email = old_email
                user.save()
            if "user_page" in locals():
                user_page.username = old_username
                user_page.save()

    return redirect("lk")


@login_required
def order(request):
    user_page = UserPage.objects.filter(user=request.user).first()

    if not user_page:
        return redirect("login")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                Subscription.objects.create(
                    user=user_page,
                    months=form.cleaned_data["months"],
                    persons=form.cleaned_data["persons"],
                    breakfast=form.cleaned_data["breakfast"],
                    lunch=form.cleaned_data["lunch"],
                    dinner=form.cleaned_data["dinner"],
                    dessert=form.cleaned_data["dessert"],
                    promocode=form.cleaned_data["promo_code"],
                )

                user_page.is_subscribed = True
                allergy_ids = request.POST.getlist("allergies", None)
                if allergy_ids:
                    user_page.allergies.set(allergy_ids)
                menu_type_id = form.cleaned_data.get("menu_type")
                if menu_type_id:
                    user_page.menu_types.add(menu_type_id)
                user_page.save()

                return redirect("lk")

            except Exception as e:
                raise Http404(f"Что-то пошло не так \n {e}")
    else:
        form = OrderForm()

    context = {
        "form": form,
        "menu_types": MenuType.objects.all(),
        "allergies": FoodTag.objects.all(),
        "user_page": user_page,
    }
    return render(request, "order.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Пароль успешно изменен!")
            return redirect("lk")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "lk.html", {"form": form})
