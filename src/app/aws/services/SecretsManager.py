import boto3
from utils import constants as C
import base64
import json

def retrieve_secret(secret_name, region=C.AWS_DEFAULT_REGION):
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

    print("secret: ", secret_dict)
    print("SecretsName", secret_name)
    
    return secret_dict


# Example usage
# secret_info = retrieve_secret("FoodShareHubSecrets")
# print(secret_info)

