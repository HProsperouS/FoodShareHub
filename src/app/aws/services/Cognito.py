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
        return "success"

    except Exception as e:
        print(e)
        return "fail"
    
def retreive_user(name:str):
    try:
        user = client.admin_get_user(UserPoolId=COGNITO_USER_POOL_ID,Username=name)
        
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
        return "success"
    except Exception as e:
        print(e)
        return "fail"
    
def generate_software_token(session:str):

    try:
        token = client.associate_software_token(Session=session)

        return token
    except Exception as e:
        print(e)
        return token
    
def verify_software_token(access_token:str,session:str,code:str):
    try:
        verify = client.verify_software_token(AccessToken=access_token,Session=session,UserCode=code)
        return verify
    except Exception as e:
        print(e)
        return verify

def login_mfa(code:str,session:str,name:str):
    try:
        verify = client.respond_to_auth_challenge(
            ClientId=COGNITO_CLIENT_ID,
            ChallengeName='SOFTWARE_TOKEN_MFA',
            ChallengeResponses={
                'USERNAME': name ,
                'SOFTWARE_TOKEN_MFA_CODE': code
            },
            Session=session  # Include the session obtained from the initiate_auth response
        )
        return verify
    except Exception as e: 
        print(e)
        return verify
