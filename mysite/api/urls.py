from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/profile', views.UserProfileView.as_view()), 
    path('users/favorites', views.UserFavoritesView.as_view()),
    path('forum', views.ArticleListView.as_view(),name='forum_all'),
    path('forum/<int:pk>', views.ArticleDetailView.as_view(), name='article_detail'),
]