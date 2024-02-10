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

    threshold = 0.6
    toxicity_score = toxic_response.get('ResultList', [{}])[0].get('Toxicity', 0)
    print(toxic_response)
    if toxicity_score > threshold:
        return True

    return False
    
# text = "Can you come my room? I want to show you something."
# text = "Fuck You Chibai"
# analyze_comprehend_toxicity(text)