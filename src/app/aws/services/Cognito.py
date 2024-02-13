import boto3
from dotenv import load_dotenv
from utils import constants as C

client = boto3.client('cognito-idp', region_name = C.AWS_DEFAULT_REGION)

def authenticate_user(name:str,password:str):
    try:
        login = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": name,
                "PASSWORD": password,
            },
            ClientId=C.COGNITO_CLIENT_ID
            )
        return [login,"success"]
    except Exception as e:
        print(e)
        if "User is disabled" in str(e):
            return "account disabled"
        return ["fail",str(e)]

def logout(access_token):
    try:
        response = client.global_sign_out(
            AccessToken=access_token
        )
        return response
    except Exception as e:
        print(e)
        return "fail"
          

def register_user(name:str,password:str,email:str,role:str,image:str,current_time:str):
    try:
        register = client.sign_up(
            ClientId = C.COGNITO_CLIENT_ID,
            Username = name,
            Password = password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {"Name": "custom:role", "Value":role},
                {'Name':"custom:image", "Value":image},
                {'Name':"custom:lastaccess","Value":current_time}
            ]
        )
        
        confirmation_mail = client.resend_confirmation_code(
            ClientId= C.COGNITO_CLIENT_ID,
            Username = name
        )
        return "success"

    except Exception as e:
        print(e)
        return "fail"
    
def retreive_user(name:str):
    try:
        user = client.admin_get_user(UserPoolId=C.COGNITO_USER_POOL_ID,Username=name)
        return user
    except Exception as e:
        print(e)

        return "fail"

def register_confirmation(name:str,code:str):
    try:
        confirmation = client.confirm_sign_up(
            ClientId = C.COGNITO_CLIENT_ID,
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
        return "fail"

def login_mfa(code:str,session:str,name:str):
    try:
        verify = client.respond_to_auth_challenge(
            ClientId=C.COGNITO_CLIENT_ID,
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
        return "fail"
    
def update_last_access(name,lastaccess):
    try:
        edit_user = client.admin_update_user_attributes(
            UserPoolId=C.COGNITO_USER_POOL_ID,
            Username=name,
            UserAttributes=[{'Name':"custom:lastaccess","Value":lastaccess}],
        )
        return edit_user

    except Exception as e:
        print(e)
        
        return "fail"
    
def update_online_status(name,status):
    try:
        edit_user = client.admin_update_user_attributes(
            UserPoolId=C.COGNITO_USER_POOL_ID,
            Username=name,
            UserAttributes=[{'Name':"custom:status","Value":status}],
        )
        return edit_user

    except Exception as e:
        print(e)
        
        return "fail"

def edit_user_information(name,email,image):
    try:
        if image == "N/A":
            updatedAttributes = [{"Name":"email",'Value':email}]
        else:
            updatedAttributes = [{'Name': "custom:image",'Value': image},{'Name': "email",'Value': email}]
        edit_user = client.admin_update_user_attributes(
            UserPoolId=C.COGNITO_USER_POOL_ID,
            Username=name,
            UserAttributes=updatedAttributes,
        )
        return edit_user

    except Exception as e:
        print(e)
        
        return "fail" 
def edit_google_user_information(name,image,role):
    try:
        updatedAttributes = [{'Name': "custom:image",'Value': image},{'Name': "custom:role",'Value': role}]
        edit_user = client.admin_update_user_attributes(
            UserPoolId=C.COGNITO_USER_POOL_ID,
            Username=name,
            UserAttributes=updatedAttributes,
        )
    except Exception as e:
        print(e)
        
    
def reset_password(current_pass,new_pass,access_token):
    try:
        reset = client.change_password(
            PreviousPassword=current_pass,
            ProposedPassword=new_pass,
            AccessToken=access_token
        )

        return "success"
    except Exception as e:
        print(e)
        if "Invalid Access Token" in str(e):
            return "Invalid Access Token"
        return "fail"
    
def disable_account(username):
    try:
        disable = client.admin_disable_user(
            UserPoolId=C.COGNITO_USER_POOL_ID,
            Username=username
        )

        return "success"
    except Exception as e:
        print(e)
        return "fail"
    
        return "fail"    

def list_cognito_user_by_usernames(usernames:list):    
    all_users = []
    for username in usernames:
        filter_string = f"username = \"{username}\""
        try:
            response = client.list_users(
                UserPoolId=C.COGNITO_USER_POOL_ID,
                Filter=filter_string
            )
            all_users.extend(response['Users'])
        except client.exceptions.ClientError as error:
            print(f"An error occurred: {error}")
    return all_users
