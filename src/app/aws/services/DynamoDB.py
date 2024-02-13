import boto3
import datetime
def login_attempts(ipaddress,username):
    # Initialize the DynamoDB client
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')

    ipaddress = ipaddress
    username = username

    # Key
    partitionKey = ipaddress + "_" + username
    key = {
        'AttemptId': {'S': partitionKey},
    }

    # Time
    current_time = datetime.datetime.now()
    five_minutes_later = current_time + datetime.timedelta(minutes=5)
    unix_timestamp = int(five_minutes_later.timestamp())

    # Define the table name
    table_name = 'RateLimiting'

    # Get a reference to the DynamoDB table
    table = dynamodb.Table(table_name)

    # Perform a scan to retrieve all items from the table
    scanTable = table.scan()
    print(scanTable)
    new_access = True
    if 'Items' in scanTable:
        items = scanTable['Items']
        for item in items:
            if item["IPAddress"] == ipaddress and item["Account"] == username:
                if int(item["Attempts"]) >= 3:
                    new_access = False
                    return "too many attempts"
                else:
                    new_access = True
                    attempts = int(item["Attempts"]) + 1
                    
                    update_expression = 'SET Attempts = :val1, TimetoReset = :val2'
                    expression_attribute_values = {
                        ':val1': {'S': str(attempts)},
                        ':val2': {'S':str(unix_timestamp)}
                    }
                    
                    # Update the item in the DynamoDB table
                    response = client.update_item(
                        TableName=table_name,
                        Key=key,
                        UpdateExpression=update_expression,
                        ExpressionAttributeValues=expression_attribute_values
                    )
                    
                    return "new attempt"
                
    if new_access == True:
        item = {
            'AttemptId': {'S': partitionKey},
            'IPAddress': {'S': ipaddress },
            'Account': {'S': username },
            'Attempts': {'S':"1"},
            'TimetoReset': {'S': str(unix_timestamp)},
        }
        
        # Put the item into the DynamoDB table
        response = client.put_item(
            TableName=table_name,
            Item=item
        )
        
        return "first attempt"
        