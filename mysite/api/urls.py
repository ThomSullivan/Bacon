from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework import permissions
from rest_framework.schemas import get_schema_view

from . import views




urlpatterns = [
    #path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/profile', views.UserProfileView.as_view()), 
    path('forum', views.ArticleListView.as_view()),
    path('forum/<int:pk>', views.ArticleDetailView.as_view()),
    path('forum/<int:pk>/comment', views.ArticleCommentView.as_view({'delete':'destroy', 'post':'create'})),
    path('champions', views.ChampionsView.as_view()),
    path('statistics', views.StatisticsView.as_view({'get':'list'})),
    path('top-ten', views.TopTenView.as_view()),
    path('routes/<str:search>', views.ResultDetailView.as_view({'get':'search'})),
    path('routes/like/<int:pk>', views.PersonLikeView.as_view({'patch':'update'})),
    path('', TemplateView.as_view(template_name='api/APIhome.html'), name='APIhome'),
    path('docs/', TemplateView.as_view(
        template_name='api/APIdocs.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='APIdocs'),
    path('openapi', get_schema_view(
        title="Six Degrees of Bacon the API",
        description="Explanation of how to interact with the REST framework availble",
        
        version="1.0.0"
    ), name='openapi-schema'),
]
