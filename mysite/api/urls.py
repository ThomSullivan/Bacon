from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/profile', views.UserProfileView.as_view()), 
    path('forum', views.ArticleListView.as_view()),
    path('forum/<int:pk>', views.ArticleDetailView.as_view()),
    path('champions', views.ChampionsView.as_view()),
    path('statistics', views.StatisticsView.as_view({'get':'list'})),
    path('top-ten', views.TopTenView.as_view()),
    path('routes', views.ResultDetailView.as_view({'get':'list','patch':'patch'}))
]