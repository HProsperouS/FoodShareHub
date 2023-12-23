# Amazon Location Service
import boto3
from utils import constants as C

def autocomplete_address(query_text, max_results=10):
    client = boto3.client('location', 
                          aws_access_key_id=C.Location_ACCESS_KEY, 
                          aws_secret_access_key=C.Location_SECRET_KEY,
                          region_name=C.Location_REGION
                          )
    
    response = client.search_place_index_for_suggestions(
        IndexName='FoodShareHub',
        Text=query_text,
        FilterCountries=["SGP"],
        MaxResults=max_results
    )

    suggestions = [result.get('Text', '') for result in response.get('Results', [])]

    return suggestions
