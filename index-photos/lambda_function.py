import boto3
import requests
import json
from requests_aws4auth import AWS4Auth
from datetime import datetime


bot = boto3.client('s3')


def lambda_handler(event, context):
    print(event)
    record = event["Records"][0]
    bucket = record['s3']['bucket']['name']
    name = record['s3']['object']['key']
    print(bucket)
    print(name)
    
    labels = getRekognitionLabel(bucket, name)
    print(labels)
    
     try:
        headerLabels = bot.head_object(Bucket=bucket, Key=name)
        print("headerLabels", headerLabels['MetaData'])
        customlabel = headerLabels['MetaData']['customLabels']
        customlabels = customlabel.split(",")
        for lab in customlabels:
            labels.append(lab)
    except:
        print("There is no custom label")
        
        
    
    doc = parsePhoto(bucket, name, labels)
    print('doc is:')
    print(doc)
    reply = transToES(doc)
    print('reply from es is:')
    print(reply)

    return {
        'statusCode' : 200,
        'body' : json.dumps("indexed successfully")
    }
    
#
# Function to generate the labels for current pic
#
def getRekognitionLabel(bucket, name):
    boto = boto3.session.Session('','',region_name='us-east-1')
    reko = boto.client('rekognition')
    response = reko.detect_labels(
        Image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : name
            }
        },
        MaxLabels=10
    )
    
    labels = []
    for res in response['Labels']:
        labels.append(res['Name'])
        labels.append(res['Name'] + 's')
    
    return labels

#
# Function to parse current pic's info as the format to be stored in Elasticsearch
#
def parsePhoto(bucket, name, labels):
    doc = {
        'objectKey' : name,
        'bucket' : bucket,
        "createdTimeStamp" : datetime.now().strftime("%y-%m-%d %H:%M:%S"),
        'labels' : labels
    }
    return doc
    

#
# Function to connect ElasticSearch and upload photo info to it
#
def transToES(doc):
    # Prepare the info for uploading
    host = 'https://search-photos-noxataj4w45hp3ldltsc456nge.us-east-1.es.amazonaws.com/photos/Photo'
    headers = { "Content-Type": "application/json" }
    response = requests.post(host, auth=("shihan", "Iamshihan1015@"), json=doc, headers=headers)
    return response
