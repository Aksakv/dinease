from django.urls import path
from .views import RestaurantListView, RestaurantDetailView
app_name = "restaurants"
urlpatterns = [
    path("", RestaurantListView.as_view(), name="restaurant-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),
]