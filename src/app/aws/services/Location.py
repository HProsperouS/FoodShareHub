# Amazon Location Service
import boto3
from utils import constants as C

client = boto3.client('location')
def autocomplete_address(query_text, max_results=10, region=C.AWS_DEFAULT_REGION):
    
    response = client.search_place_index_for_suggestions(
        IndexName='FoodShareHubIndex',
        Text=query_text,
        FilterCountries=["SGP"],
        MaxResults=max_results
    )

    suggestions = [result.get('Text', '') for result in response.get('Results', [])]

    return suggestions

def get_current_user_location(longitude,latitude):
    try:
        # Call the SearchPlaceIndexForPosition operation
        response = client.search_place_index_for_position(
            IndexName='FoodShareHubIndex',  # Replace with your place index name
            Position=[longitude, latitude],  # Specify longitude first, then latitude
            MaxResults=1  # Limit the number of results to 1
        )

        # Extract the place name from the response
        place_name = response['Results'][0]['Place']['Label']
        
        return place_name
    
    except Exception as e:
        print(f"Error: {e}")
        return "fail"
