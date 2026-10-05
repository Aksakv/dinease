from django.views.generic import ListView, DetailView

from .models import Restaurant
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    next_page = reverse_lazy("restaurants:restaurant-list")
    
class RestaurantListView(ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list.html"
    context_object_name = "restaurants"


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurants/restaurant_detail.html"
    context_object_name = "restaurant"