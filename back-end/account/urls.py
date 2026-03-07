from django.urls import path
from .views import (
    MyProfileView,
    ProfileDetailView,
    ProfileSearchView,
)

urlpatterns = [
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('search/', ProfileSearchView.as_view(), name='profile-search'),
    path('<str:username>/',
         ProfileDetailView.as_view(), name='profile-detail'),
]