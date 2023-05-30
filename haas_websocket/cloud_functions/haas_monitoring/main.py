import os
import settings
from datetime import datetime, timedelta
import logging
from google.cloud import storage, secretmanager_v1, bigquery
from google.oauth2 import service_account
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, find_dotenv

smtp_server = ""
sender_email = ""
receiver_emails = ""
username = ""
password = ""

def set_clients():
    global _bigquery_client, _rtdh_gcs_client
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    key_path = "gcp_credentials.json"
    credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    
    _bigquery_client = bigquery.Client(credentials = credentials, project=settings.ADAP_PROJECT_ID)
    _rtdh_gcs_client = storage.Client(credentials = credentials, project=settings.RTDH_PROJECT_ID)

def load_config():
    global smtp_server, sender_email, receiver_emails, username, password
    load_dotenv()
    smtp_server = os.environ['SMTP_SERVER_IP'] 
    sender_email = os.environ['SMTP_EMAIL']
    receiver_emails = os.environ['EMAIL_RECIPIENTS'] 
    username = os.environ['SMTP_USERNAME'] 
    password = os.environ['SMTP_PASSWORD']

def query_adap(table_name, count_field, timestamp_field, date):
    full_table_name = f'{settings.HAAS_ALERT_RAW_TABLE_NAME}.{table_name}'
    print(full_table_name)
    
    QUERY = (f'SELECT count({count_field}) as count \
             FROM `{full_table_name}` \
             WHERE DATE({timestamp_field}) = "{date}"')
    query_job = _bigquery_client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    
    for row in rows:
        count = row['count']
    
    return count


def query_gcs(data_type, year, month, day):
    bucket = _rtdh_gcs_client.bucket(settings.RTDH_STORAGE_BUCKET_NAME)
    sub_folder = f'{data_type}/{settings.SCHEMA_VERSION}/year={year}/month={month}/day={day}/'
    blobs = list(bucket.list_blobs(prefix=sub_folder, delimiter='/'))
    number_of_files = len(blobs)
    return number_of_files

def generate_row(count, row_style):
    html = f'<tr style="{row_style}">\n' \
        f'<td>{count["DATE"]}</td>\n' \
        f'<td>{count["TYPE"]}</td>\n' \
        f'<td>{count["BQ"]}</td>\n' \
        f'<td>{count["GCS"]}</td>\n' \
        '</tr>\n'
    return html

def create_table_html(count_data):
    if len(count_data) == 0:
        return ''
    
    html = '<table class="dataframe">\n' \
           '<table>\n' \
           '<thead>\n' \
           '<tr style="text-align: center;background-color: #b0dfff;">\n' \
           '<th style="padding: 12px;">Date</th>\n' \
           '<th style="padding: 12px;">Count Type</th>\n' \
           '<th style="padding: 12px;">BQ Count</th>\n' \
            '<th style="padding: 12px;">GCS Count</th>\n' \
           '</tr>\n' \
           '</thead>\n' \
           '<tbody>\n'
    
    i = 0
    for count in count_data:
        row_style = 'text-align: center;background-color: #f2f2f2;' if i % 2 == 1 else 'text-align: center;'

        html += generate_row (count, row_style)
        i += 1
    
    html += '</tbody>\n' \
            '</table>'

    return html

def create_table():
    date_obj = datetime.now() - timedelta(1)
    date = date_obj.strftime('%Y-%m-%d')
    logging.info(f"Creating count tables for {date}")
    count_list = []
    adap_dict = {}
    gcs_dict = {}
    
    day = date_obj.strftime("%d")
    month = date_obj.strftime("%m")
    year = date_obj.strftime("%Y")
        
    count_field = "type"
    timestamp_field = "timestamp"
    adap_dict['Heartbeat'] = query_adap(settings.HEARTBEAT_TABLE, count_field, timestamp_field, date)
    gcs_dict['Heartbeat'] = query_gcs("heartbeat", year, month, day)
    
    count_field = "external_id"
    timestamp_field = "start_time"
    adap_dict['Location'] = query_adap(settings.LOCATION_TABLE, count_field, timestamp_field, date)
    gcs_dict['Location'] = query_gcs("location", year, month, day)

    count_field = "id"
    timestamp_field = "timestamp"
    adap_dict['Point'] = query_adap(settings.POINT_TABLE, count_field, timestamp_field, date)
    gcs_dict['Point'] = query_gcs("point", year, month, day)

    count_field = "external_id"
    timestamp_field = "last_heartbeat"
    adap_dict['Thing'] = query_adap(settings.THING_TABLE, count_field, timestamp_field, date)
    gcs_dict['Thing'] = query_gcs("thing", year, month, day)

    for type in adap_dict:
        data = {
            'DATE': "",
            'TYPE': "",
            'BQ': "",
            'GCS': ""
        }
        data["DATE"] = date
        data["TYPE"] = type
        data["BQ"] = (str(adap_dict[type]))
        data["GCS"] = (str(gcs_dict[type]))
        count_list.append(data)
        
    count_html = create_table_html(count_list)
    return count_html


def create_email_content():
    html = f'<h2>{str(settings.ENVIRONMENT).upper()} GCP Count Report</h2>'
    html += create_table()

    return html

def email_daily_counts():
    try:
        port = 587
        message = MIMEMultipart()
        message["Subject"] = f"{str(settings.ENVIRONMENT).upper()} CDOT HAAS Counts"
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