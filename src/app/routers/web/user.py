# import third-party libraries
from io import BytesIO
from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    RedirectResponse,
)
from pydantic import BaseModel

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from depends import (
    USER_RBAC,
    RBAC_TYPING,
    RBACResults,
)
from aws.services import (
    edit_user_information,
    reset_password,
    disable_account,
    upload_qrcode_to_s3,
    delete_s3_object,
    upload_userimage_to_s3
)
from utils import constants as C
import pyotp
import qrcode

from aws.services import (
    generate_software_token,
    verify_software_token
)

from aws.services import(
    upload_to_s3,
)

from utils.helper import (
    decode_base64_file
)
from utils import constants as C
# TESTING FOR PERSONALIZE
import boto3
import json
import time

#TESTING FOR LOCATION
import datetime

# Class Objects
class MFASetupCode(BaseModel):
    AccessToken: str
    Session:str
    Code:str

class UserImage(BaseModel):
    FileName: str
    ContentType: str
    Size: int
    Base64: str

class EditUser(BaseModel):
    Email: str
    Image: UserImage

class ResetPassword(BaseModel):
    CurrentPassword: str
    NewPassword: str
class LocationDistanceTime(BaseModel):
    TargetLocation: str
    CurrentLocation: str

user_router = APIRouter(
    include_in_schema=True,
    tags= ["User"]
)
RBAC_DEPENDS = Depends(USER_RBAC, use_cache=False)

@user_router.post("/user/filteritems")
async def filteritems(request: Request, formData: LocationDistanceTime) -> ORJSONResponse:
    try:
       # Find location
        print(formData)
        target = formData.TargetLocation
        current = formData.CurrentLocation

        client = boto3.client('location', region_name='ap-southeast-1')

        response_index1 = client.search_place_index_for_text(
            IndexName='FoodShareHubIndex',
            Text=target
        )
        response_index2 = client.search_place_index_for_text(
            IndexName='FoodShareHubIndex',
            Text=current
        )

        # Extract longitude and latitude from the response
        location1 = response_index1['Results'][0]['Place']['Geometry']['Point']
        location2 = response_index2['Results'][0]['Place']['Geometry']['Point']
        print(datetime.datetime.now())
        response = client.calculate_route(
            CalculatorName='explore.route-calculator.Grab',
            DeparturePosition=[location2[0], location2[1]],
            DestinationPosition=[location1[0], location1[1]],
            TravelMode="Bicycle",
            DepartureTime=datetime.datetime.now() 
        )
        # Options
        # TravelMode='Car'|'Truck'|'Walking'|'Bicycle'|'Motorcycle'
        # OptimizeFor='FastestRoute'|'ShortestRoute',

        # Extract distance and duration from the response
        distance = response['Summary']['Distance']
        duration = response['Summary']['DurationSeconds'] 
        minutes, seconds = divmod(duration, 60)
        formatted_duration = f"{int(minutes)} mins {int(seconds)} seconds"
        print(distance)
        print(formatted_duration)


        return ORJSONResponse(
            content={"distance":distance,"duration":formatted_duration}
        )
    except Exception as e:
        print(e)

@user_router.get("/user")
async def defaultpage(request:Request,rbac_res: RBAC_TYPING=RBAC_DEPENDS) -> HTMLResponse:

    # Find location
    client = boto3.client('location', region_name='ap-southeast-1')

    response_index1 = client.search_place_index_for_text(
        IndexName='FoodShareHubIndex',
        Text="Hougang ave 8 Block 650"
    )
    response_index2 = client.search_place_index_for_text(
        IndexName='FoodShareHubIndex',
        Text="Marina Bay Sands"
    )

    # Extract longitude and latitude from the response
    location1 = response_index1['Results'][0]['Place']['Geometry']['Point']
    location2 = response_index2['Results'][0]['Place']['Geometry']['Point']
    print(datetime.datetime.now())
    response = client.calculate_route(
        CalculatorName='explore.route-calculator.Grab',
        DeparturePosition=[location2[0], location2[1]],
        DestinationPosition=[location1[0], location1[1]],
        TravelMode="Bicycle",
        DepartureTime=datetime.datetime.now()  # You can specify a departure time, e.g., '2022-01-01T12:00:00Z'
    )
    # Options
    # TravelMode='Car'|'Truck'|'Walking'|'Bicycle'|'Motorcycle'
    # OptimizeFor='FastestRoute'|'ShortestRoute',

    # Extract distance and duration from the response
    distance = response['Summary']['Distance']
    duration = response['Summary']['DurationSeconds']
    minutes, seconds = divmod(duration, 60)
    formatted_duration = f"{int(minutes)} mins {int(seconds)} seconds"
    # convert = str(datetime.timedelta(seconds = duration))
    # print(convert)
    print(distance)
    print(response)
    print(formatted_duration)

    return await render_template(
        name="index.html",
        context={
            "request": request,
            "location":{"distance":distance,"duration":formatted_duration}
    },
)

@user_router.get("/usertest")
async def usertest(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        print(rbac_res.headers)
        return rbac_res
    
    
    # legs = response['Legs']
    # coordinates = []
    # for leg in legs:
    #     for point in leg['Points']:
    #         coordinates.append(point['Position'])
    # print(coordinates)

    # print(location)
    
    # personalizeRt = boto3.client('personalize-runtime')
    # personalize = boto3.client('personalize')

    # response = personalize.list_recipes()

    # for recipe in response['recipes']:
    #     print (recipe)
    
    # schema = {
    #     "type": "record",
    #     "name": "Interactions",
    #     "namespace": "com.amazonaws.personalize.schema",
    #     "fields": [
    #         {
    #             "name": "USER_ID",
    #             "type": "string"
    #         },
    #         {
    #             "name": "ITEM_ID",
    #             "type": "string"
    #         },
    #         {
    #             "name": "TIMESTAMP",
    #             "type": "long"
    #         }
    #     ],
    #     "version": "1.0"
    # }
    # USE WHEN NEED NEW SCHEMA
    # create_interactions_schema_response = personalize.create_schema(
    #     name='getting-started-schema',
    #     schema=json.dumps(schema)
    # )
    # interactions_schema_arn = create_interactions_schema_response['schemaArn']
    # print(json.dumps(create_interactions_schema_response, indent=2))

    # USE WHEN HAVE EXISITING SCHEMA
    # get_schema = personalize.list_schemas(
    #     maxResults=1
    # )
    # print(get_schema)
    # interactions_schema_arn = get_schema["schemas"][0]["schemaArn"]
    # print(interactions_schema_arn)

    # CREATE WHEN NEED NEW GROUP
    # response = personalize.create_dataset_group(name = 'testgroup')
    # dataset_group_arn = response['datasetGroupArn']
    # description = personalize.describe_dataset_group(datasetGroupArn = dataset_group_arn)['datasetGroup']

    # print('DATASETGROUP Name: ' + description['name'])
    # print('DATASETGROUP ARN: ' + description['datasetGroupArn'])
    # print('DATASETGROUP Status: ' + description['status'])

    # USED WHEN HAVE EXISITING GROUP
    # dataset_group_arn = 'arn:aws:personalize:ap-southeast-1:654654435792:dataset-group/testgroup'
    # print("COMPLETE ALREADY 1111111111111")

    # # CAN BE DONE IN CONSOLE
    # response = personalize.create_dataset(
    #     name = 'testdata',
    #     schemaArn = interactions_schema_arn,
    #     datasetGroupArn = dataset_group_arn,
    #     datasetType = 'Interactions'
    # )

    # dataset_arn = response['datasetArn']

    # # NEED TO WAIT FOR DATASET TO FINISH CREATING BEFORE RUNNING
    # # CAN BE DONE IN CONSOLE
    # response = personalize.create_dataset_import_job(
    #     jobName = 'TestJob',
    #     datasetArn = dataset_arn,
    #     dataSource = {'dataLocation':'s3://foodsharehub-bucket/datasets/ratings.csv'},
    #     roleArn = 'arn:aws:iam::654654435792:role/PersonalizeRole',
    #     importMode = 'FULL'
    # )

    # dataset_interactions_import_job_arn = response['datasetImportJobArn']

    # description = personalize.describe_dataset_import_job(
    # datasetImportJobArn = dataset_interactions_import_job_arn)['datasetImportJob']

    # print('JOB Name: ' + description['jobName'])
    # print('JOB ARN: ' + description['datasetImportJobArn'])
    # print('JOB Status: ' + description['status'])

    # print("COMPLETE ALREADY 2222222222")

    # max_time = time.time() + 3*60*60 # 3 hours
    # while time.time() < max_time:
    #     describe_dataset_import_job_response = personalize.describe_dataset_import_job(
    #         datasetImportJobArn = dataset_interactions_import_job_arn
    #     )
    #     status = describe_dataset_import_job_response["datasetImportJob"]['status']
    #     print("Interactions DatasetImportJob: {}".format(status))
        
    #     if status == "ACTIVE" or status == "CREATE FAILED":
    #         break
            
    #     time.sleep(60)


    # create_solution_response = personalize.create_solution(
    #     name='solution name', 
    #     recipeArn= 'arn:aws:personalize::2912629:recipe/aws-user-personalization', 
    #     datasetGroupArn = description['datasetGroupArn']
    #     )
    # solution_arn = create_solution_response['solutionArn']
    # print('solution_arn: ', solution_arn)

    # create_solution_version_response = personalize.create_solution_version(
    #     solutionArn = solution_arn
    # )

    # solution_version_arn = create_solution_version_response['solutionVersionArn']
    # print(json.dumps(create_solution_version_response, indent=2))

    # max_time = time.time() + 3*60*60 # 3 hours
    # while time.time() < max_time:
    #     describe_solution_version_response = personalize.describe_solution_version(
    #         solutionVersionArn = solution_version_arn
    #     )
    #     status = describe_solution_version_response["solutionVersion"]["status"]
    #     print("SolutionVersion: {}".format(status))
        
    #     if status == "ACTIVE" or status == "CREATE FAILED":
    #         break
            
    #     time.sleep(60)
    
    # response = personalize.create_campaign(
    #     name = 'campaign name',
    #     solutionVersionArn = 'solution version arn'
    # )

    # arn = response['campaignArn']

    # description = personalize.describe_campaign(campaignArn = arn)['campaign']
    # print('CAMPAIGN Name: ' + description['name'])
    # print('CAMPAIGN ARN: ' + description['campaignArn'])
    # print('CAMGAIGN Status: ' + description['status'])

    # response = personalizeRt.get_recommendations(
    #     campaignArn = description['campaignArn'],
    #     userId = '123',
    #     numResults = 10
    # )

    # print("Recommended items")
    # for item in response['itemList']:
    #     print (item['itemId'])

    return await render_template(
        name="user/test.html",
        context={
            "request": request,
        },
    )

@user_router.get("/user/account")
async def account(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res
            
    return await render_template( 
        name="user/account.html",
        context={
            "request": request,
        },
    )

@user_router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    
    try:
        request.session.clear()
        # clear from redis
        # elasticache.delete(request.get("session")["username"])

        return RedirectResponse("/login", status_code=303)
    except Exception as e:
        print(e)

@user_router.post("/enablemfa")
def enablemfa(request:Request) -> ORJSONResponse:
    try:
        bucket_name = C.S3_BUCKET_NAME 
        name = request.session.get("session")["username"]
        session = request.session.get("session")["session_id"]
        # generate associate token to verify later
        associate = generate_software_token(session=session)
        session = associate["Session"]
        verify_access_token = associate["SecretCode"]

        print("Start generating QR Code")

        otp = pyotp.TOTP(verify_access_token)
        auth_str = otp.provisioning_uri(name=name,issuer_name="FoodShareHub")
        qrImg = qrcode.make(auth_str)
        imgPath = "uploads/" + name + "_qrcode.png"

        publicAccessURL = f"https://{bucket_name}.s3.amazonaws.com/{imgPath}"

        buffer = BytesIO()
        qrImg.save(buffer, "PNG")
        buffer.seek(0) 

        upload = upload_qrcode_to_s3(buffer,imgPath)

        print("QR Code generated")  
    
        return ORJSONResponse(
            content={"qr_code":publicAccessURL ,"access_token":verify_access_token,"session":session,"status":"success"}
        )

    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"qr_code": "N/A","access_token":"N/A","session":"N/A","status":"fail"}
        )

@user_router.post("/verifymfa")
def verifymfa(request:Request,formData:MFASetupCode) -> ORJSONResponse:
    try:

        access_token = formData.AccessToken
        session = formData.Session
        code = formData.Code
        username = request.session.get("session")["username"]
        verify = verify_software_token(access_token,session,code)

        if verify == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )

        request.session.get("session")["mfa"] = "Enabled"

        path = "uploads/" + username + "_qrcode.png"
        delete = delete_s3_object(path)

        return ORJSONResponse(
            content={"status":"success"}
        )
    
    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/account/editInformation")
async def edit_information(request:Request, formData:EditUser) -> ORJSONResponse:
    try:
        # Temp S3 Info
        bucket_name = C.S3_BUCKET_NAME

        session = request.session.get("session")
        username = session["username"]
        email = session["email"]
        publicAccessURL = "N/A"
        try:    
            user_filename= username + "_" + formData.Image.FileName
            file = decode_base64_file(formData.Image.Base64)
            
            if upload_userimage_to_s3(file, user_filename, bucket_name, formData.Image.ContentType):
                print("Image uploaded to S3 successfully")
            else:
                return ORJSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)
            
            publicAccessURL = f"https://{bucket_name}.s3.amazonaws.com/user/{user_filename}"
        except Exception as e:
            print(e)

        # Update user profile attributes
        updated_user = edit_user_information(username,email,publicAccessURL)

        if updated_user == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        request.session["session"]["image"] = publicAccessURL

        return ORJSONResponse(
            content={"image":publicAccessURL,"status":"success"}
        )
    
    except Exception as e :
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/password/reset")
async def reset_user_password(request:Request, formData:ResetPassword) -> ORJSONResponse:
    try:
        current_pass = formData.CurrentPassword
        new_pass = formData.NewPassword
        access_token = request.session["session"]["session_id"]

        reset = reset_password(current_pass,new_pass,access_token)

        if reset == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        return ORJSONResponse(
            content={"status":"success"}
        )
    


    except Exception as e:
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/account/disable")
async def reset_user_password(request:Request) -> ORJSONResponse:
    try:

        username = request.session["session"]["username"]
        reset = disable_account(username)

        if reset == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        return ORJSONResponse(
            content={"status":"success"}
        )
    
    except Exception as e:
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )
