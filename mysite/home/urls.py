from django.urls import path
from django.views.generic import TemplateView
from . import views
#from routes.views import ResultListView, result

app_name = 'home'

urlpatterns = [
    path('', views.homeView, name='home'),
    path('user/<int:pk>/',   views.ProfileDetailVeiw.as_view(template_name='home/profile.html'), name='profile'),
    path('topten/', views.top_ten, name='topten'),
    path('statistics/', views.statistics, name='statistics'),
    path('explain/', TemplateView.as_view(template_name='home/explain.html'), name='explain'),
    path('champions/', views.champions, name='champions'),
    path('user/manage/', views.accountManageView, name='manage'),
    path('user/getToken', TemplateView.as_view(template_name='home/getToken.html'), name='getToken'),
    path('contact-me/', views.contactMe, name='contact'),
    path('whoami/', TemplateView.as_view(template_name='home/whoami.html'), name='whoami'),
    path('donate/', views.donate, name='donate'),
    path('create-payment-intent', views.create_payment, name='create_payment'),
    path('donate/success', views.donate_success, name='donate_success'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook')
    
]