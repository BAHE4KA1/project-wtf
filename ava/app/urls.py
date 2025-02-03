from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('add/', team_add),
    path('reg/', register_page),
    path('login/', login_page),
    # path('<str:room_name>/', room, name='room'),
    path('change_id/', set_id),
    path('users/', get_users),
    path('users/<str:app_id>/', get_user)
]
