import boto3
from dotenv import load_dotenv
import os

load_dotenv()

COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_HOSTED_UI = os.environ.get("COGNITO_HOSTED_UI")

client = boto3.client('cognito-idp',region_name = 'us-east-1')

def authenticate_user(name:str,password:str):
    try:
        login = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": name,
                "PASSWORD": password,
            },
            ClientId=COGNITO_CLIENT_ID
            )
        return login
    except Exception as e:
        print(e)
        

def register_user(name:str,password:str,email:str,role:str):
    try:
        register = client.sign_up(
            ClientId = COGNITO_CLIENT_ID,
            Username = name,
            Password = password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {"Name": "custom:role", "Value":role}
            ]
        )

        confirmation_mail = client.resend_confirmation_code(
            ClientId= COGNITO_CLIENT_ID,
            Username = name
        )

        return register

    except Exception as e:
        print(e)
    
def retreive_user(accesstoken:str):
    try:
        user = client.get_user(AccessToken=accesstoken)
        
        return user
    except Exception as e:
        print(e)

def register_confirmation(name:str,code:str):
    try:
        confirmation = client.confirm_sign_up(
            ClientId = COGNITO_CLIENT_ID,
            Username = name,
            ConfirmationCode = code
        )
    except Exception as e:
        print(e)