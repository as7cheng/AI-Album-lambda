import boto3
import json
import requests

def lambda_handler(event, context):
    photos = []
    message = event["queryStringParameters"]["q"]
    keys = toLext(message)
    print(keys)
    search = parseSearch(keys)
    print(search)
    photos = esSearch(search)
    print(photos)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': json.dumps(photos),
        'isBase64Encoded': False
    }
    
    
def toLext(message):
    lex = boto3.client('lex-runtime')
    keys = lex.post_text(
        botName = 'nlp_album',
        botAlias = 'albumTest',
        userId = 'key',
        inputText = message)
    return keys

def parseSearch(keys):
    search = []
    if keys["slots"]["first"] != None:
        search.append(keys["slots"]["first"])
    if keys["slots"]["second"] != None:
        search.append(keys["slots"]["second"])
    return search


def esSearch(search):
    photos = []
    for key in search:
        host = 'https://search-photos-noxataj4w45hp3ldltsc456nge.us-east-1.es.amazonaws.com'
        url = host + '/photos/_search?q=' + key
        headers = {'Content-Type' : 'application/json'}
        reply = requests.get(url, headers=headers, auth=("shihan", "Iamshihan1015@")).json()
        for item in reply["hits"]["hits"]:
            bucket = item["_source"]["bucket"]
            key = item["_source"]["objectKey"]
            photoURL = "https://{0}.s3.amazonaws.com/{1}".format(bucket,key)
            if photoURL not in photos:
                photos.append(photoURL)
    return photos
    