"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from recipe_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("card1/", views.card1, name="card1"),
    path("card2/", views.card2, name="card2"),
    path("card3/", views.card3, name="card3"),
    path("lk/", views.lk, name="lk"),
    path("order/", views.order, name="order"),
    path("registration/", views.registration, name="registration"),
    path("admin/", admin.site.urls),
<<<<<<< Updated upstream
=======
    path("recipe/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path('shopping-list/<int:recipe_id>/', views.shopping_list, name='shopping_list'),
    path('recipe/<int:recipe_id>/feedback/', views.recipe_feedback, name='recipe_feedback'),
    path('lk/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('lk/profile_update/', views.profile_update, name='profile_update'),
    path('lk/change_password/', views.change_password, name='change_password'),
>>>>>>> Stashed changes
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
