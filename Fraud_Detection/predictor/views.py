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

# Load the trained model
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zwg_credit_card_fraud_pipeline.pkl')
model = joblib.load(model_path)


def _style_form_fields(form, *, password_autocomplete=None):
    """Apply TailwindCSS friendly classes to Django auth forms."""
    base_classes = (
        "w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 "
        "placeholder-slate-500 shadow-sm focus:border-emerald-400 focus:outline-none "
        "focus:ring-2 focus:ring-emerald-400/60"
    )
    for name, field in form.fields.items():
        existing = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f"{base_classes} {existing}".strip()
        field.widget.attrs.setdefault('placeholder', field.label)
        if field.widget.input_type == 'password' and password_autocomplete:
            field.widget.attrs['autocomplete'] = password_autocomplete
        elif field.widget.input_type == 'text':
            field.widget.attrs.setdefault('autocomplete', 'username')

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
        _style_form_fields(form, password_autocomplete='new-password')
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to 'home' after successful registration
    else:
        form = UserCreationForm()
        _style_form_fields(form, password_autocomplete='new-password')
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
        aggregates = transactions.aggregate(total=Sum('amt'), avg=Avg('amt'))
        fraud_aggregates = transactions.filter(is_fraud=True).aggregate(total=Sum('amt'))
        context['total_amount'] = aggregates['total'] or 0
        context['average_amount'] = aggregates['avg'] or 0
        context['fraud_amount'] = fraud_aggregates['total'] or 0

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.all()
        fraud_transactions = transactions.filter(is_fraud=True)

        context.update({
            'total_transactions': transactions.count(),
            'fraud_transaction_count': fraud_transactions.count(),
            'total_amount': transactions.aggregate(total=Sum('amt'))['total'] or 0,
            'fraud_amount': fraud_transactions.aggregate(total=Sum('amt'))['total'] or 0,
            'recent_transactions': transactions.order_by('-processed_at')[:5],
        })
        return context

def login_view(request):
    """URL: /login/"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        _style_form_fields(form, password_autocomplete='current-password')
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to 'home' after successful login
    else:
        form = AuthenticationForm()
        _style_form_fields(form, password_autocomplete='current-password')
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
    fraud_transactions = transactions.filter(is_fraud=True)
    fraud_transactions_json = json.dumps(list(fraud_transactions.values('latitude', 'longitude', 'province')))

    fraud_by_region_qs = fraud_transactions.values('province').annotate(count=Count('province')).order_by('-count')
    fraud_by_region = list(fraud_by_region_qs)
    max_fraud_region_count = max((item['count'] for item in fraud_by_region), default=0)

    total_transactions = transactions.count()
    fraud_count = fraud_transactions.count()
    aggregates = transactions.aggregate(total=Sum('amt'), avg=Avg('amt'))
    fraud_aggregates = fraud_transactions.aggregate(total=Sum('amt'))
    total_amount = aggregates['total'] or 0
    avg_amount = aggregates['avg'] or 0
    fraud_amount = fraud_aggregates['total'] or 0

    top_merchants = list(
        transactions.values('merchant')
        .annotate(total_spend=Sum('amt'), transaction_count=Count('transaction_id'))
        .order_by('-transaction_count', '-total_spend')[:5]
    )

    recent_transactions = list(transactions[:8])
    recent_fraud = list(fraud_transactions[:5])

    context = {
        'recent_transactions': recent_transactions,
        'recent_fraud': recent_fraud,
        'fraud_transactions_json': fraud_transactions_json,
        'fraud_by_region': fraud_by_region,
        'max_fraud_region_count': max_fraud_region_count,
        'total_transactions': total_transactions,
        'fraud_count': fraud_count,
        'legit_count': total_transactions - fraud_count,
        'fraud_percentage': (fraud_count / total_transactions * 100) if total_transactions else 0,
        'total_amount': total_amount,
        'avg_amount': avg_amount,
        'fraud_amount': fraud_amount,
        'top_merchants': top_merchants,
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
