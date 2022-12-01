from django.urls import path
from django.views.generic import TemplateView
from . import views
#from routes.views import ResultListView, result

app_name='routes'
urlpatterns = [
    path('search/', views.search_pk),
    path('result/<int:pk>/', views.ResultDetailView.as_view(), name='result'),
    path('result/<int:pk>/favorite/',
        views.AddFavoriteView.as_view(), name='person_favorite'),
    path('result/<int:pk>/unfavorite/',
        views.DeleteFavoriteView.as_view(), name='person_unfavorite'),
    path('bacon/', TemplateView.as_view(template_name='routes/bacon.html'))
]