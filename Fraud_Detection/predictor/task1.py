from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .services.email_service import send_fraud_alert
from models import Transaction
import time

def check_transactions():
    recent_frauds = Transaction.objects.filter(
        is_fraud=True, 
        notification_sent=False
    ).all()
    
    for transaction in recent_frauds:
        send_fraud_alert(transaction)
        transaction.notification_sent = True
        transaction.save()

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(check_transactions, 'interval', minutes=1, id='check_fraud')
    scheduler.start()