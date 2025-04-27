<<<<<<< Updated upstream
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm, LoginForm, CustomPasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging
from django.db import transaction
from django.core.validators import validate_email


from .models import User
from .models import Recipe, Ingredient, UserPage, DailyMenu, UserPage


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
>>>>>>> Stashed changes


def index(request):
    context = {}
    return HttpResponse(render(request, "index.html", context))


def user_login(request):
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("lk")
    return render(request, "auth.html")


<<<<<<< Updated upstream
=======
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
            "user_page": userpage
        },
    )


@login_required
def recipe_feedback(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user_page = get_object_or_404(UserPage, user=request.user)
        liked = 'liked' in request.POST
        disliked = 'disliked' in request.POST
        
        if liked:
            if recipe in user_page.disliked_recipes.all():
                user_page.disliked_recipes.remove(recipe)
            user_page.liked_recipes.add(recipe)
        elif disliked:
            if recipe in user_page.liked_recipes.all():
                user_page.liked_recipes.remove(recipe)
            user_page.disliked_recipes.add(recipe)
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


>>>>>>> Stashed changes
def user_logout(request):
    logout(request)
    return redirect("login")


def card1(request):
    context = {}
    return render(request, "card1.html", context)


<<<<<<< Updated upstream
def card2(request):
    context = {}
    return render(request, "card2.html", context)
=======
def lk_view(request):
    user_page = UserPage.objects.filter(user=request.user).first()
    today_menu = user_page.today_menu if user_page else None
    avatar = user_page.image
>>>>>>> Stashed changes


def card3(request):
    context = {}
    return render(request, "card3.html", context)

<<<<<<< Updated upstream

def lk(request):
    context = {}
    return render(request, "lk.html", context)
=======
    context = {
        'recipes': recipes,
        'user_page': user_page,
        'persons_count': persons_count,
        'allergies_info': allergies_info,
        'calories': int(calories),
        'meals_count': meals_count,
        'avatar': avatar,
        'menu_type': today_menu.menu_type,
    }
    return render(request, 'lk.html', context)
  
@login_required
def upload_avatar(request):
    user_page = UserPage.objects.filter(user=request.user).first()
>>>>>>> Stashed changes

    if request.method == 'POST':
        if 'image' not in request.FILES:
            messages.error(request, "Файл не был загружен")
            return redirect('lk')
        
        user_page.image = request.FILES['image']
        user_page.save()
        messages.success(request, "Аватар успешно обновлён")
        return redirect('lk')
    
    return redirect('lk')

@login_required
def profile_update(request):
    if request.method == 'POST':
        try:
            user = request.user
            user_page = UserPage.objects.filter(user=request.user).first()
            
            old_email = user.email
            old_username = user_page.username if hasattr(user_page, 'username') else ''
            
            new_username = request.POST.get('username', old_username)
            new_email = request.POST.get('email', old_email).lower().strip()
            
            
            if new_email != old_email and User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                raise ValueError("Этот email уже используется другим пользователем")
            
            user_page.username = new_username
            user.email = new_email
            
            with transaction.atomic():
                user.save()
                user_page.save()
                
            messages.success(request, "Данные успешно обновлены")
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            messages.error(request, "Произошла ошибка при обновлении данных")
            
            if 'user' in locals():
                user.email = old_email
                user.save()
            if 'user_page' in locals():
                user_page.username = old_username
                user_page.save()
    
    return redirect('lk')

def order(request):
    context = {}
    return render(request, "order.html", context)


<<<<<<< Updated upstream
def registration(request):
    context = {}
    return render(request, "registration.html", context)
=======
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('lk')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'lk.html', {'form': form})
>>>>>>> Stashed changes
