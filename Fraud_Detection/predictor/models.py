# predictor/models.py
from datetime import datetime
from django.db import models

class FraudDetection(models.Model):
    fraud_detection_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    result = models.BooleanField()
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.fraud_detection_id)

    class Meta:
        db_table = 'fraud_detection'

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    merchant = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    amt = models.FloatField()
    gender = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city_pop = models.IntegerField()
    job = models.CharField(max_length=100)
    unix_time = models.BigIntegerField()
    merch_latitude = models.FloatField()
    merch_longitude = models.FloatField()
    processed_at = models.DateTimeField(default=datetime.now)
    is_fraud = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.merchant} - {self.amt} - {self.is_fraud}"
    