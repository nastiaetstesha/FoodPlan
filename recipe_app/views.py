from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


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


def registration(request):
    context = {}
    return render(request, "registration.html", context)
