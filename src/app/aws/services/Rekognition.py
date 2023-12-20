import boto3
import botocore

rekognition_client = boto3.client('rekognition')

def detect_objects(image_bytes):

    # Use DetectLabels API to identify the object
    response = rekognition_client.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=5,  
        MinConfidence=70  
    )

    # Get detected labels
    labels = [{'Name': label['Name'], 'Confidence': label['Confidence']} for label in response['Labels']]

    # Determine if inappropriate tags are included
    inappropriate_labels = {'Violence', 'Explicit Nudity', 'Drugs'}
    contains_inappropriate = any(label['Name'] in inappropriate_labels for label in labels)

    return labels, contains_inappropriate


def detect_objects_and_moderate(image_bytes):
    # Use DetectModerationLabels API to identify potential inappropriate content
    response_moderation = rekognition_client.detect_moderation_labels(
        Image={'Bytes': image_bytes},
        MinConfidence=70
    )

    # Get detected moderation labels
    moderation_labels = response_moderation.get('ModerationLabels', [])

    # If no moderation labels are detected, use DetectLabels API to identify normal objects
    if not moderation_labels:
        response_labels = rekognition_client.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=5,
            MinConfidence=70
        )

        # Get detected labels
        labels = [{'Name': label['Name'], 'Confidence': label['Confidence']} for label in response_labels['Labels']]

        # Return normal labels and set contains_inappropriate to False
        # return labels, [], False
        return labels, []

    # Determine if inappropriate tags are included
    # inappropriate_labels = {'Violence', 'Explicit Nudity', 'Drugs'}
    # contains_inappropriate = any(label['Name'] in inappropriate_labels for label in moderation_labels)
    # return [], moderation_labels, contains_inappropriate

    return [], moderation_labels


