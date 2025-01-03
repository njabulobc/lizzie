# predictor/urls.py
from django.urls import path
from . import views
from .views import DashboardView, TransactionDetailView, UserProfileView

urlpatterns = [
    path('', views.home, name='home'),
    path('api/predict/', views.predict_fraud, name='predict_fraud'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transaction/<int:transaction_id>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
