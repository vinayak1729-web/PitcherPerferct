import os
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv
load_dotenv()
# Replace with your actual environment variable name
email_sender = 'vinayak.test.001@gmail.com'
email_password = os.environ.get("EMAIL_PASSWORD")
email_receiver = ''
if not email_password:
    raise ValueError("EMAIL_PASSWORD environment variable not set or incorrect.")

subject = 'Check Out My New Video'
body = """
hi {email_receiver}
auto email genereated from Surya prabha india 
"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Email sent successfully!")
except smtplib.SMTPAuthenticationError as e:
    print("Authentication error:", e)
except Exception as e:
    print("An error occurred:", e)