# import third-party libraries
from argon2 import (
    PasswordHasher, 
    Type as Argon2Type,
)

import boto3
import base64
import json

# import Python's standard libraries
import pathlib
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = True
APP_ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()
STATIC_PATH = APP_ROOT_PATH.joinpath("static")
FAVICON_PATH = STATIC_PATH.joinpath("favicon.ico")

PASSWORD_HASHER = PasswordHasher(
    encoding="utf-8",
    time_cost=4,         # 4 count of iterations
    salt_len=64,         # 64 bytes salt
    hash_len=64,         # 64 bytes hash
    parallelism=4,       # 4 threads
    memory_cost=64*1024, # 64MiB
    type=Argon2Type.ID   # using hybrids of Argon2i and Argon2d
)

# Application constants
DOMAIN = "https://localhost:8080" if DEBUG_MODE else "https://deployed.live"
FLASH_MESSAGES = "_messages"
SESSION_COOKIE = "session"
API_PREFIX = "/api"
ERROR_TABLE = {
    400: {
        "title": "400 - Bad Request",
        "description": "The request was invalid"
    },
    401: {
        "title": "401 - Unauthorized",
        "description": "The requested resource is unauthorized"
    },
    403: {
        "title": "403 - Forbidden",
        "description": "The requested resource is forbidden"
    },
    404: {
        "title": "404 - Page Not Found",
        "description": "The requested resource was not found"
    },
    405: {
        "title": "405 - Method Not Allowed",
        "description": "The method is not allowed for the requested URL"
    },
    418: {
        "title": "I'm a teapot",
        "description": "I'm a teapot"
    },
    422: {
        "title": "422 - Unprocessable Entity",
        "description": "Unprocessable entity"
    },
    429: {
        "title": "429 - Too Many Requests",
        "description": "Too many requests, please slow down and try again later",
    },
    500: {
        "title": "500 - Internal Server Error",
        "description": "Internal server error"
    },
    503: {
        "title": "503 - Service Unavailable",
        "description": "Service unavailable"
    },
    504: {
        "title": "504 - Gateway Timeout",
        "description": "Gateway timeout"
    },
    505: {
        "title": "505 - HTTP Version Not Supported",
        "description": "HTTP version not supported"
    },
    511: {
        "title": "511 - Network Authentication Required",
        "description": "Network authentication required"
    },
}

# User Roles
GUEST = "Guest"
USER = "User"
ADMIN = "Admin"
ALLROLES = (GUEST, USER, ADMIN)

# AWS Congfig
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# AWS Cognito Configuration
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

# AWS Secrets Manager Configuration
SECRETS_MANAGER_SECRET_NAME = os.getenv("SECRETS_MANAGER_SECRET_NAME")

# SSH Tunnel Configuration (for connecting to the database)
SSH_TUNNEL_HOST = os.getenv("SSH_TUNNEL_HOST")  # Bastion Host IP or DNS
SSH_TUNNEL_SSH_PORT = 22  
SSH_TUNNEL_USERNAME = os.getenv("SSH_TUNNEL_USERNAME")
SSH_TUNNEL_PASSWORD = os.getenv("SSH_TUNNEL_PASSWORD")  

# RDS Configuration (for connecting to the database)
def retrieve_secret(secret_name, region=AWS_DEFAULT_REGION):
    """
    Retrieve a secret from AWS Secrets Manager.

    Parameters:
    secret_name (str): The name of the secret to retrieve.
    region (str): The AWS region name, defaults to 'ap-southeast-1'.

    Returns:
    dict: A dictionary containing the contents of the secret.
    """
    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region)

    # Retrieve the secret
    response = client.get_secret_value(SecretId=secret_name)

    # Parse the secret value
    if 'SecretString' in response:
        secret = response['SecretString']
        secret_dict = json.loads(secret)
    else:
        # If the secret is in binary format, you would handle it here
        # This example assumes it's always a string
        decoded_binary_secret = base64.b64decode(response['SecretBinary'])
        secret_dict = json.loads(decoded_binary_secret)

    return secret_dict

secret_dict = retrieve_secret(SECRETS_MANAGER_SECRET_NAME)
DB_HOST = secret_dict['host']
DB_PORT = 5432  
DB_USER = secret_dict['user']
DB_PASSWORD = secret_dict['password']
DB_NAME = secret_dict['db']
