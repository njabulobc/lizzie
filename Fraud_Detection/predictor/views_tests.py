from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .views import DashboardView
from .models import Transaction
from datetime import datetime
import json

class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Base transaction data
        self.transaction_data = {
            'merchant': 'Test Shop',
            'category': 'Shopping',
            'amt': 100.00,
            'gender': 'M',
            'city': 'Test City',
            'province': 'TC',
            'latitude': 0.0,
            'longitude': 0.0,
            'city_pop': 100000,
            'job': 'Tester',
            'unix_time': int(datetime.now().timestamp()),
            'merch_latitude': 0.0,
            'merch_longitude': 0.0,
        }

    def test_empty_dashboard(self):
        """Test dashboard with no transactions"""
        view = DashboardView()
        context = view.get_context_data()
        
        self.assertEqual(context['total_transactions'], 0)
        self.assertEqual(context['fraud_count'], 0)
        self.assertEqual(context['fraud_percentage'], 0)
        self.assertEqual(context['transaction_by_category'], '{}')

    def test_dashboard_with_transactions(self):
        """Test dashboard with mix of transactions"""
        # Create 3 regular and 2 fraud transactions
        for _ in range(3):
            Transaction.objects.create(**self.transaction_data, is_fraud=False)
        
        fraud_data = self.transaction_data.copy()
        fraud_data['category'] = 'Online'
        for _ in range(2):
            Transaction.objects.create(**fraud_data, is_fraud=True)

        view = DashboardView()
        context = view.get_context_data()
        
        self.assertEqual(context['total_transactions'], 5)
        self.assertEqual(context['fraud_count'], 2)
        self.assertEqual(context['fraud_percentage'], 40.0)

        # Verify category data
        category_data = json.loads(context['transaction_by_category'])
        self.assertEqual(category_data['Shopping'], 3)
        self.assertEqual(category_data['Online'], 2)

    def test_dashboard_category_distribution(self):
        """Test category distribution calculation"""
        # Create transactions with different categories
        categories = ['Shopping', 'Food', 'Food', 'Travel']
        
        for category in categories:
            transaction_data = self.transaction_data.copy()
            transaction_data['category'] = category
            Transaction.objects.create(**transaction_data, is_fraud=False)

        view = DashboardView()
        context = view.get_context_data()
        
        category_data = json.loads(context['transaction_by_category'])
        self.assertEqual(category_data['Shopping'], 1)
        self.assertEqual(category_data['Food'], 2)
        self.assertEqual(category_data['Travel'], 1)