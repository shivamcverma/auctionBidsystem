from django.urls import path
from myapp import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_page, name="login_page"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/signup/", views.signup_view, name="signup"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("place-bid/<int:item_id>/", views.place_bid, name="place_bid"),
    path("add-product/", views.add_product, name="add_product"),
]