from django.urls import path
from .views import *


urlpatterns = [
    path('', index),
    path('add/', team_add),
    path('reg/', reg),
    path('login/', login_page),
]