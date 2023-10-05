
"""
 serializeImageData:  Lambda function to serialize the image data
"""
import json
import boto3
import base64
s3 = boto3.client('s3')
def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]
    # Download the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key, "/tmp/image.png")
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())
    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




"""
ImageClassifier : Lambda function to predict image classification
"""
import json
import sagemaker
import base64
import sagemaker.session as session  # Import sagemaker.session module
from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-10-01-06-17-04-128"  # Replace with your actual endpoint name
session = session.Session()
def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["body"]["image_data"])  # Assuming the image data is passed in the "image" field of the input event
    # Instantiate a Predictor
    predictor = sagemaker.predictor.Predictor(endpoint_name=ENDPOINT, sagemaker_session=session)  # Create a Predictor for your endpoint

    # For this model, the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction
    inferences = predictor.predict(image)  # Send the image data to the endpoint for inference

    # We return the data back to the Step Function
    event["body"]["inferences"] = json.loads(inferences.decode('utf-8'))  # Encode the inferences as base64
    print(event)
    return {
        'statusCode': 200,
        'body': event
    }



"""
InferenceConfidenceFilter : Lambda function tofiter inference results based on confidence
"""
import json


THRESHOLD = .93

def lambda_handler(event, context):
    # Get the inferences from the event
    inferences = event["body"]['body']['inferences']
    
    # Check if any values in any inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }