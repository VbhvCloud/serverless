import os
import json
import requests
import time
from boto3 import resource
import logging

logger = logging.getLogger("lambda")

def lambda_handler(event, context):
    try:
        # Extract necessary information from the SNS event
        # sns_message = event
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        image_path = sns_message['image_path']
        image_name = sns_message['image_name']
        user_email = sns_message['user_email']
        status = sns_message['status']
        message = sns_message['message']

        if status:
            email_status(user_email, "Your file has been uploaded successfully: {} at {}".format(image_name, image_path))
        else:
            email_status(user_email, message)

        
    except Exception as e:
        logger.error("Error while handling data : {}".format(str(e)))


def email_status(user_email, message):
        
    try:
        # Your Mailgun API key and domain
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")

        # Mailgun sender email address
        sender = os.getenv("MAILGUN_SENDER")

        # Mailgun API endpoint for sending emails
        mailgun_api_url = f'https://api.mailgun.net/v3/{mailgun_domain}/messages'

        subject = 'Upload Status Notification'
        body_text = 'The status of your upload is:\n\n {} \n\n Thanks,\nVaibhav Mahajan'.format(message)


        # Create the API request
        response = requests.post(
            mailgun_api_url,
            auth=('api', mailgun_api_key),
            data={
                'from': sender,
                'to': user_email,
                'subject': subject,
                'text': body_text
            }
        )

        # Check if the email was sent successfully
        if response.status_code == 200:
            print(f'Email sent successfully to {user_email}')
        else:
            print(f'Failed to send email. Status code: {response.status_code}')

        track_email(os.getenv("DYNAMODB_TABLE"), user_email, body_text)
    except Exception as e:
        logger.error("Error while sending email : {}".format(str(e)))

def track_email(table_name, user_email, message):
    try:
        # Use AWS DynamoDB to track emails sent
        dynamodb = resource('dynamodb', region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(table_name)

        item_id = str(int(time.time()))

        table.put_item(
            Item={
                'id': int(item_id),
                'UserEmail': user_email,
                'Timestamp': str(time.time()),
                'Mesaage': message
            }
        )
    except Exception as e:
        logger.error("Error while tracking mail : {}".format(str(e)))
        
# data = {
# }
# lambda_handler(data, "ee")