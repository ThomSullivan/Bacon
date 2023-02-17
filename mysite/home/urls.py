from django.urls import path
from django.views.generic import TemplateView
from .views import ProfileDetailVeiw, top_ten, statistics, champions, homeView, accountManageView, contactMe
#from routes.views import ResultListView, result

app_name = 'home'

urlpatterns = [
    path('', homeView, name='home'),
    path('user/<int:pk>/',   ProfileDetailVeiw.as_view(template_name='home/profile.html'), name='profile'),
    path('topten/', top_ten, name='topten'),
    path('statistics/', statistics, name='statistics'),
    path('explain/', TemplateView.as_view(template_name='home/explain.html'), name='explain'),
    path('champions/', champions, name='champions'),
    path('user/manage/', accountManageView, name='manage'),
    path('user/getToken', TemplateView.as_view(template_name='home/getToken.html'), name='getToken'),
    path('contact-me/', contactMe, name='contact'),
    path('whoami/', TemplateView.as_view(template_name='home/whoami.html'), name='whoami'),
    path('donation/', TemplateView.as_view(template_name='home/donation.html'), name='donation'),
]