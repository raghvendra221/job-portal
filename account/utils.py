import threading
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_custom_email(subject, template_name, context, to_email):
    from_email = settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject, 
        body=text_content, 
        from_email=from_email,
         to= [to_email],
         )
    email.attach_alternative(html_content, 'text/html')
     # ✅ Run email sending in a separate thread
    threading.Thread(target=email.send).start()