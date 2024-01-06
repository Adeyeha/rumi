from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search_roommates/', views.search_roommates, name='search_roommates'),
    path('user_detail/<int:user_id>/', views.user_detail, name='user_detail'),
    path('accept_interest/<int:interest_id>/', views.accept_view, name='accept_interest'),
    path('reject_interest/<int:interest_id>/', views.reject_view, name='reject_interest'),
    path('request-connection/<int:user_id>/', views.request_connection, name='request_connection'),
    path("chat_list/", views.chat_list, name="chat_list"),
    path("chat/<str:room_name>/", views.chat, name="chat"),
    path('email-verify/<email_token>/',views.email_verify, name='email_verify'),

    ]
