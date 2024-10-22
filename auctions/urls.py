from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_list", views.new_list, name="new_list"),
    path("listing/<int:id>", views.listing_details, name="listing_details"),
    path("comment/<int:id>", views.commentView, name="comment"),
    path('auction/<int:auction_id>/update_price/', views.update_price, name='update_price'),
    path("closeAuction/<int:id>", views.closeAuction, name="closeAuction"),
    path("watchlist",views.watchlist_view, name="watchlist"),
    path("watchlist/<int:auction_id>", views.watchlist_add, name="watchlist_add"),
    path("category/<str:category>", views.categories, name="category_index"),
]
