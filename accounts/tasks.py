from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@shared_task
def send_verification_email_task(subject, template, context, recipient):
    html_content = render_to_string(template, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Your OTP is here",  # fallback text
        from_email='nitandhraerp@gmail.com',
        to=[recipient],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()