from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils import timezone
from jinja2 import Environment, FileSystemLoader
from datetime import timedelta
import smtplib
import psycopg2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import json

def days_ago(n):
    return timezone.utcnow() - timedelta(days=n)

# Load Jinja template environment
env = Environment(loader=FileSystemLoader('/opt/airflow/dags/templates'))

# DAG default args
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

def send_to_telegram(message: str):
    try:
        token = Variable.get("TELEGRAM_BOT_TOKEN")
        chat_ids = json.loads(Variable.get("TELEGRAM_CHAT_IDS"))
        print(f"Using Telegram token: {token} and chat IDs: {chat_ids}")
        for chat_id in chat_ids:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload)
            print(f"Telegram response for {chat_id}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

def send_bill_reminders():
    # Load vars
    db_config = {
        'host': Variable.get("DB_HOST"),
        'port': Variable.get("DB_PORT"),
        'dbname': Variable.get("DB_NAME"),
        'user': Variable.get("DB_USER"),
        'password': Variable.get("DB_PASSWORD"),
    }

    print("Connecting to database with config:", db_config)

    smtp_host = Variable.get("SMTP_HOST")
    smtp_port = int(Variable.get("SMTP_PORT"))
    email_sender = Variable.get("EMAIL_SENDER")
    email_password = Variable.get("EMAIL_PASSWORD")

    print(f"Using SMTP server: {smtp_host}:{smtp_port} for sender {email_sender}")

    # Connect to DB
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    query = """
    SET TIMEZONE TO 'Asia/Jakarta';
    SELECT u.full_name, u.email, rb.due_date, rb.amount
    FROM users u
    JOIN bookings b ON u.user_id = b.user_id
    JOIN recurring_bills rb ON b.booking_id = rb.booking_id
    WHERE rb.is_paid = FALSE
    AND rb.due_date::date = CURRENT_DATE + INTERVAL '10 days';
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Fetched {len(rows)} rows from the database.")

    if not rows:
        print("✅ No upcoming bills found.")
        return

    # Load HTML template
    template = env.get_template('email_template.html')

    for full_name, email, due_date, amount in rows:
        html_content = template.render(
            full_name=full_name,
            due_date=due_date.strftime('%Y-%m-%d'),
            amount=f"{amount:,.2f}"
        )

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "⏰ Kosan Payment Reminder"
        msg['From'] = email_sender
        msg['To'] = email
        print(f"Preparing email for {full_name} <{email}>: Due {due_date.strftime('%Y-%m-%d')}, Amount {amount:,.2f}")
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(email_sender, email_password)
                server.sendmail(email_sender, email, msg.as_string())
            print(f"✅ Reminder sent to: {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")

    cursor.close()
    conn.close()

# Define DAG
with DAG(
    dag_id='bill_reminder_email_dag',
    description='Send bill reminders for unpaid kosan bookings',
    default_args=default_args,
    schedule='0 8 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['billing', 'email']
) as dag:
    send_reminder_emails = PythonOperator(
        task_id='send_bill_reminder_emails',
        python_callable=send_bill_reminders
    )