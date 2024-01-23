# Amazon Location Service
import boto3
from utils import constants as C

def autocomplete_address(query_text, max_results=10):
    client = boto3.client('location')
    
    response = client.search_place_index_for_suggestions(
        IndexName='FoodShareHubIndex',
        Text=query_text,
        FilterCountries=["SGP"],
        MaxResults=max_results
    )

    suggestions = [result.get('Text', '') for result in response.get('Results', [])]

    return suggestions
