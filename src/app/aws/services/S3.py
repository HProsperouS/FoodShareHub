from io import BytesIO
import boto3
import botocore
from utils import constants as C

# Method to upload file to S3
def upload_to_s3(file_data, file_name, bucket_name, content_type):
    try:
        s3 = boto3.client('s3')
        folder_path = "uploads/"
        s3.upload_fileobj(file_data, bucket_name, 
                          f"{folder_path}{file_name}", 
                          ExtraArgs={'ContentType': content_type})
        return True
    except botocore.exceptions.ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False

def upload_userimage_to_s3(file_data, file_name, bucket_name, content_type):
    try:
        s3 = boto3.client('s3')
        folder_path = "user/"
        s3.upload_fileobj(file_data, bucket_name, f"{folder_path}{file_name}", ExtraArgs={'ContentType': content_type})
        return True
    except botocore.exceptions.ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False
    
def upload_qrcode_to_s3(buffer,imgPath):
    try:
        bucket_name = C.S3_BUCKET_NAME
        s3 = boto3.client('s3')
        s3.upload_fileobj(buffer,bucket_name,imgPath)
        return True
    except botocore.exceptions.ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False
    
def delete_s3_object(imgPath):
    try:
        bucket_name = C.S3_BUCKET_NAME
        s3 = boto3.client("s3")
        s3.delete_object(Bucket=bucket_name, Key=imgPath)
    except botocore.exceptions.ClientError as e:
        print(f"Error deleting from S3: {e}")
        return False