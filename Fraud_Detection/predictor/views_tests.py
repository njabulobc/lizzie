from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .views import DashboardView
from .models import Transaction
from datetime import datetime
import json
import pytz

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
            'processed_at': datetime.now(pytz.UTC),
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


class PredictFraudAPITests(TestCase):
    def setUp(self):
        self.url = reverse('predict_fraud')
        self.base_payload = {
            'merchant': 'API Shop',
            'category': 'Electronics',
            'amt': 250.75,
            'gender': 'F',
            'city': 'API City',
            'province': 'AC',
            'latitude': 12.34,
            'longitude': 56.78,
            'city_pop': 150000,
            'job': 'Analyst',
            'unix_time': int(datetime.now().timestamp()),
            'merch_latitude': 12.30,
            'merch_longitude': 56.70,
            'processed_at': datetime.now(pytz.UTC).isoformat(),
        }

    def test_probability_persisted_and_returned(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.base_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)

        self.assertIn('probability', payload)
        self.assertIn('prediction', payload)
        self.assertIn('top_factors', payload)
        self.assertIsInstance(payload['top_factors'], list)

        transaction = Transaction.objects.latest('transaction_id')
        self.assertAlmostEqual(transaction.fraud_probability, payload['probability'], places=4)
        self.assertEqual(transaction.is_fraud, payload['prediction'])
        self.assertGreaterEqual(payload['probability'], 0.0)
        self.assertLessEqual(payload['probability'], 1.0)
