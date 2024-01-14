from .S3 import (
    upload_to_s3
)

from .Rekognition import (
    detect_objects,
    detect_objects_and_moderate
)

from .Location import (
    autocomplete_address
)

from .Cognito import(
    register_user,
    register_confirmation,
    retreive_user,
    authenticate_user,
    generate_software_token,
    verify_software_token,
    login_mfa,
    list_cognito_user_by_usernames,
)