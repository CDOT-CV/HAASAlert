import os
import settings
from datetime import datetime, timedelta
import logging
from google.cloud import storage, secretmanager_v1, bigquery
from google.oauth2 import service_account
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = ""
sender_email = ""
receiver_emails = ""
username = ""
password = ""

def set_clients():
    global _bigquery_client
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    key_path = "gcp_credentials.json"
    credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    _bigquery_client = bigquery.Client(credentials = credentials, project=settings.PROJECT_ID)

def load_config():
    global smtp_server, include_adap_counts, sender_email, receiver_emails, username, password
    smtp_server = os.environ['SMTP_SERVER_IP'] 
    sender_email = os.environ['SMTP_EMAIL']
    receiver_emails = os.environ['EMAIL_RECIPIENTS'] 
    username = os.environ['SMTP_USERNAME'] 
    password = os.environ['SMTP_PASSWORD']

def generate_header_html():
    html = '<table>\n' \
        '<thead>\n' \
        '<tr style="text-align: center;background-color: #b0dfff;">\n' \
        '<th style="padding: 12px;">Date</th>\n' \
        '<th style="padding: 12px;">Thing ID</th>\n' \
        '<th style="padding: 12px;">Heartbeat Count</th>\n' \
        '</tr>\n' \
        '</thead>\n'
    return html

def generate_data_row(count, row_style):
    html = f'<tr style="{row_style}">\n' \
        f'<td>{count["DATE"]}</td>\n' \
        f'<td>{count["ID"]}</td>\n' \
        f'<td>{count["HEARTBEAT_COUNT"]}</td>\n' \
        '</tr>\n'
    return html

def create_count_table_html(count_data):
    if len(count_data) == 0:
        return ''
    
    html = '<table class="dataframe">\n' \
            f'{generate_header_html()}' \
            '<tbody>\n'
    
    i = 0
    for count in count_data:
        row_style = 'text-align: center;background-color: #f2f2f2;' if i % 2 == 1 else 'text-align: center;'

        html += generate_data_row (count, row_style)
        i += 1
    
    html += '</tbody>\n' \
            '</table>'

    return html

def query_adap(table_name, date):
    full_table_name = f'{settings.HAAS_ALERT_RAW_TABLE_NAME}.{table_name}'
    
    QUERY = (f'SELECT thing.id,  count(type) as count FROM `{full_table_name}` WHERE DATE(timestamp) = "{date}" group by thing.id')
    query_job = _bigquery_client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    log_dict = {}
    for row in rows:
        log_dict[row.id] = row.count
    return log_dict

def create_count_table(date):
    logging.info(f"Creating count tables for {date}")

    counts = query_adap(settings.HEARTBEAT_TABLE, date)
    count_list = []
    
    for id in counts:
        data = {
            'DATE': [],
            'ID': [],
            'HEARTBEAT_COUNT': []
        }
        data["DATE"] = date
        data["ID"] = id
        
        data["HEARTBEAT_COUNT"] = (str(counts[id]))
        count_list.append(data)
        
    count_html = create_count_table_html(count_list)
    return count_html

def create_email_content():
    date = datetime.now() - timedelta(1)
    date = date.strftime('%Y-%m-%d')
    html = f'<h2>{str(settings.PROJECT_ID).upper()} GCP Count Report {date}</h2>'
    
    table = create_count_table(date)
    html += table

    return html

def email_daily_counts():
    try:
        port = 587
        message = MIMEMultipart()
        message["Subject"] = f"{str(settings.PROJECT_ID).upper()} CDOT HAAS Heartbeat Counts"
        message["From"] = sender_email # use the same email for sender
        message["To"] = receiver_emails 
        
        body = create_email_content()
        message.attach(MIMEText(body, "html"))

        context = ssl._create_unverified_context()
        smtp = smtplib.SMTP(smtp_server, port)
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        smtp.sendmail(sender_email,
        receiver_emails.split(","),
        message.as_string())
        logging.info("Email sent")
        smtp.quit()

        logging.info("Email sent successfully")
    except Exception as e:
        logging.exception(e)

def entry(request):
    set_clients()
    load_config()
    email_daily_counts()
    return ("Email cloud function has been run", 200)
            
if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    _bigquery_client = ""
    entry("")