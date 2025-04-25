from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm


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

