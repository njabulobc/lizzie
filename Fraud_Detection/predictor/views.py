# predictor/views.py
from collections import Counter
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView
import pytz
from django.db.models import Count, Sum, Avg
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer
import joblib
import json
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the trained model
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zwg_credit_card_fraud_pipeline.pkl')
model = joblib.load(model_path)

@api_view(['POST'])
def predict_fraud(request):
    """URL: /api/predict/"""
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        transaction = serializer.save()
        harare_tz = pytz.timezone('Africa/Harare')
        if transaction.processed_at.tzinfo is None:
            transaction.processed_at = harare_tz.localize(transaction.processed_at)
            transaction.save()
        # Prepare the data for prediction
        transaction_data = serializer.data
        data = {
            'merchant': [transaction_data['merchant']],
            'category': [transaction_data['category']],
            'amt': [transaction_data['amt']],
            'gender': [transaction_data['gender']],
            'city': [transaction_data['city']],
            'province': [transaction_data['province']],
            'latitude': [transaction_data['latitude']],
            'longitude': [transaction_data['longitude']],
            'city_pop': [transaction_data['city_pop']],
            'job': [transaction_data['job']],
            'unix_time': [transaction_data['unix_time']],
            'merch_latitude': [transaction_data['merch_latitude']],
            'merch_longitude': [transaction_data['merch_longitude']],
            'processed_at': [transaction_data['processed_at']]
        }
        df = pd.DataFrame(data)

        # Extract additional features
        df['processed_at'] = pd.to_datetime(df['processed_at'])
        if df['processed_at'].dt.tz is None:
            df['processed_at'] = df['processed_at'].dt.tz_localize(pytz.UTC)
        else:
            df['processed_at'] = df['processed_at'].dt.tz_convert(pytz.UTC)
        df['hour'] = df['processed_at'].dt.hour
        df['day_of_week'] = df['processed_at'].dt.dayofweek
        df['month'] = df['processed_at'].dt.month
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        # Drop the 'processed_at' column as it's no longer needed
        df = df.drop(columns=['processed_at'])

        # Make prediction
        prediction = model.predict(df)
        transaction.is_fraud = prediction[0]
        transaction.save()
        return Response({'prediction': prediction[0]}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def register(request):
    """URL: /register/"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to 'home' after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.all()
        
        total_count = transactions.count()
        fraud_count = transactions.filter(is_fraud=True).count()
        
        context['total_transactions'] = total_count
        context['fraud_count'] = fraud_count
        context['fraud_percentage'] = (fraud_count / total_count * 100) if total_count > 0 else 0
        
        # Category data
        category_data = dict(transactions.values('category')
                           .annotate(count=Count('category'))
                           .values_list('category', 'count'))
        context['transaction_by_category'] = json.dumps(category_data)
        
        return context
    
    
class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transaction_detail.html'
    context_object_name = 'transaction'
    pk_url_kwarg = 'transaction_id'


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'

def login_view(request):
    """URL: /login/"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to 'home' after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """URL: /logout/"""
    logout(request)
    return redirect('login')

def custom_404_view(request, exception):
    return render(request, 'predictor/error404.html', {'error_code': 404, 'error_message': 'Page Not Found'})

@login_required
def home(request):
    """URL: /"""
    transactions = Transaction.objects.all().order_by('-processed_at')
    fraud_transactions = transactions.filter(is_fraud=True).values('latitude', 'longitude', 'province')
    fraud_transactions_json = json.dumps(list(fraud_transactions))

 # Count fraud transactions by region
    fraud_by_region = fraud_transactions.values('province').annotate(count=Count('province')).order_by('-count')

    #Debug statements
    logger.debug(fraud_transactions)
    logger.debug(fraud_by_region)
    print(fraud_by_region)
    print(type(fraud_by_region))

    context = {
        'transactions': transactions,
        'fraud_transactions_json': fraud_transactions_json,
        'fraud_by_region' : fraud_by_region,
    }
    return render(request, 'home.html', context)

@login_required
def about(request):
    """URL: /about/"""
    return render(request, 'about.html')

def contact(request):
    """URL: /contact/"""
    return render(request, 'contact.html')

def error_404_view(request, exception):
    return render(request, 'predictor/error404.html', {'error_code': 404, 'error_message': 'Page Not Found'})
