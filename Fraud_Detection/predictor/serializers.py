# predictor/serializers.py
from rest_framework import serializers
from .models import FraudDetection, Transaction

class FraudDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudDetection
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
    
    def validate_amt(self, value):
        if value <= 0:
            raise serializers.ValidationError("Transaction amount must be positive")
        return value
    
    def validate(self, data):
        if 'latitude' in data and (data['latitude'] < -90 or data['latitude'] > 90):
            raise serializers.ValidationError("Invalid latitude")
        if 'longitude' in data and (data['longitude'] < -180 or data['longitude'] > 180):
            raise serializers.ValidationError("Invalid longitude")
        return data