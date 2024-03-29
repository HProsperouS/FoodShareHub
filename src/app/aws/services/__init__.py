from .S3 import (
    upload_to_s3,
    upload_qrcode_to_s3,
    delete_s3_object,
    upload_userimage_to_s3
)

from .Rekognition import (
    detect_objects,
    detect_objects_and_moderate
)

from .Location import (
    autocomplete_address,
    get_current_user_location
)

from .SecretsManager import (
    retrieve_secret
)

from .Cognito import(
    register_user,
    register_confirmation,
    retreive_user,
    authenticate_user,
    generate_software_token,
    verify_software_token,
    login_mfa,
    edit_user_information,
    reset_password,
    disable_account,
    list_cognito_user_by_usernames,
    edit_google_user_information,
    update_last_access,
    update_online_status,
    edit_google_user_information,
    logout
)

from .SES import(
    email_lastaccess,
    email_message_not_viewed,
    verify_email_address
    
)

from .Comprehend import (
    analyze_comprehend_toxicity
)

from .DynamoDB import (
    login_attempts
)