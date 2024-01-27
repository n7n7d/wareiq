from celery import Celery
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

celery_app = Celery('tasks', broker='redis://localhost:6379/0')


@celery_app.task(name='send_sms')
def send_sms(data):
    url = "https://www.fast2sms.com/dev/bulkV2"
    querystring = { 
        "authorization": "n5IL39OPtZHqblT6z1joV24MiuheE0mdYcQ8pRWSakJNCGsAXfsP3kMGocUjYL0iK5VFl6EWgI7O91ba", 
        "message": f"Status for {data.get('order_id')} is {data.get('order_status')}", 
        "language": "english", 
        "route": "q", 
        "numbers": "8894628232,"} 
    
    headers = { 
        'cache-control': "no-cache"
    } 
    try: 
        response = requests.get(url, 
                                    headers = headers, 
                                    params = querystring) 
        
        return f"SMS Successfully Sent: {response.text}"
    except Exception as error: 
        return f"Oops! Something wrong : {error}"



@celery_app.task(name='send_email')
def send_email(data):
    sender_email = "nischay007@gmail.com"
    receiver_email = data.get('email')
    password = "eoqu lbls oghn jjfw" 
    subject = "Order Status Notification"
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    html_content = data.get('template')
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"
    finally:
        server.quit()