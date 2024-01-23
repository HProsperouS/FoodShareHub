import boto3
import botocore

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