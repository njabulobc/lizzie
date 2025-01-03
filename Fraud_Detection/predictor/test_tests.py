from django.test import TestCase, Client
from django.urls import reverse
from predictor.models import Transaction
from datetime import datetime

class TransactionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_transaction = Transaction.objects.create(
            merchant="Amazon",
            category="Online Shopping",
            amt=1000.00,
            gender="M",
            city="New York",
            province="NY",
            latitude=40.7128,
            longitude=-74.0060,
            city_pop=8419000,
            job="Engineer",
            unix_time=int(datetime.now().timestamp()),
            merch_latitude=40.7128,
            merch_longitude=-74.0060,
            is_fraud=False
        )

    def test_transaction_creation(self):
        """Test transaction creation"""
        transaction = Transaction.objects.get(transaction_id=self.test_transaction.transaction_id)
        self.assertEqual(transaction.merchant, "Amazon")
        self.assertEqual(transaction.amt, 1000.00)
        self.assertEqual(transaction.is_fraud, False)

    def test_transaction_update(self):
        """Test transaction update"""
        self.test_transaction.amt = 2000.00
        self.test_transaction.save()
        updated_transaction = Transaction.objects.get(transaction_id=self.test_transaction.transaction_id)
        self.assertEqual(updated_transaction.amt, 2000.00)

    def test_fraud_flag(self):
        """Test fraud flag functionality"""
        self.test_transaction.is_fraud = True
        self.test_transaction.save()
        self.assertTrue(Transaction.objects.get(transaction_id=self.test_transaction.transaction_id).is_fraud)