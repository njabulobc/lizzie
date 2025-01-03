from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from threading import Thread

def send_fraud_alert_async(transaction):
    Thread(target=send_fraud_alert, args=(transaction,)).start()

def send_fraud_alert(transaction):
    subject = 'Fraud Alert: Suspicious Transaction Detected'
    html_message = render_to_string('emails/fraud_alert.html', {
        'transaction': transaction,
    })
    
    try:
        send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['egutsa08@gmail.com'],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")