import boto3
from dotenv import load_dotenv
from utils import constants as C

client = boto3.client('ses', region_name = C.AWS_DEFAULT_REGION)
def verify_email_address(email_address):
    try:
        response = client.verify_email_identity(
            EmailAddress=email_address
        )
        print("Verification email sent to", email_address)
        return response
    except Exception as e:
        print(e)
        return "fail"

def email_message_not_viewed(sender,receiver,message,receiver_email):
    try:
        sender_email = 'tayzheyin123@gmail.com'
        subject = 'You have just received a Notification'
        body_html = """<html>
        <head></head>
            <body>
            <div>
                <h1>Message from """ + sender + """</h1>
                <p>Hello """ + receiver + """,</p>
                <p>You have just received a message in your inbox.</p>
                <p>Message : """ + message + """</p>
                
            </div>
            </body>
        </html>"""

        response = client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [receiver_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    
                    'Html': {'Data': body_html}
                }
            }
        )
        return response
    except Exception as e:
        print(e)
        return "fail"


def email_lastaccess(receiver_email:str,name:str,lastaccess:str):
    try:
        # Set up email parameters
        sender_email = 'tayzheyin123@gmail.com'
        recipient_email = receiver_email
        subject = 'Test Email'
        body_text = 'This is a test email sent using AWS SES.'
        body_html = """<html>
        <head></head>
            <body>
            <div>
                <h1>Last Access Alert</h1>
                <p>Hello """ + name + """,</p>
                <p>Your account was last accessed on """ + lastaccess + """.</p>
                <p>If you don't access your account within a week, it will be temporarily disabled.</p>
                <p>Thank you.</p>
            </div>
            </body>
        </html>"""

        # Send email
        response = client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        return response

    except Exception as e:
        print(e)
        return "fail"


        