import boto3

def analyze_comprehend_toxicity(text):  

    comprehend = boto3.client(service_name='comprehend', region_name="us-east-1")

    toxic_response = comprehend.detect_toxic_content(
        TextSegments=[
            {
                'Text': text
            }
        ], 
        LanguageCode='en'
    )

    threshold = 0.7
    toxicity_score = toxic_response.get('ResultList', [{}])[0].get('Toxicity', 0)
    if toxicity_score > threshold:
        return True
    
    # Labels Method (Not used)
    # labels = toxic_response.get('ResultList', [{}])[0].get('Labels', [])
    # for label in labels:
    #     if label['Score'] > threshold:
    #         # If any score is above the threshold, return a True, means the content is toxic
    #         return True

    return False
    
# text = "Can you come my room? I want to show you something."
# detect_malicious_content(text)