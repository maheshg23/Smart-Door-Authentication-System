import json
import logging
import boto3
from datetime import datetime
from datetime import timedelta
import random



def sendSMS(phone,faceId,otp):
    sns = boto3.client('sns', region_name = 'us-east-1')
    url = "https://smartdoorauthentication.s3.amazonaws.com/OTPlogin.html?faceId="+faceId
    message = "Your OTP is - " + str(otp) + "\n\n Click here to enter OTP " + url
    print(message)
    try:
        res = sns.publish(
            PhoneNumber = phone,
            Message = message,
            MessageStructure = 'string'
            )
    except KeyError:
        print("error in sending sms")
        
        
def generateOTP():
    return random.randint(1000,9999)    

def putToDynamoDbPasscodes(table, faceId):
    epochafter5 = int(datetime.now().timestamp()) + 300
    otp = generateOTP()
    table.put_item(
        Item={
            'faceID' : faceId,
            'ExpirationTimeStamp' : epochafter5,
            'CurrentTimeStamp' : (epochafter5 - 300),
            'OTP' :otp
            })
    return otp    
    
def getTimeStamp(fileName):
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket = 'smartdoor-visitor-faces',
        Key = fileName
    )
    return response['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
    
def putToDynamoDbVisitors(table,faceId,name,phone,fileName):
    table.put_item(
        Item={
            'faceId': faceId,
            'name': name,
            'phone': phone,
            'photos': {
                'objectKey' : fileName,
                'bucket' : "smartdoor-visitor-faces",
                'createdTimestamp' : getTimeStamp(fileName)
                },
            'account_type': 'standard_user',
        }
    )
    
def connectToDB(tableName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    print(table.creation_date_time)
    return table
    
def extractInformation(event):
    request = event["message"]
    #faceId = request["faceId"]
    name = request["name"]
    phone = request["phone"]
    fileName = request["fileName"]
    return name, phone, fileName

def indexFaceRekognition(buffer,name):
    rek = boto3.client('rekognition')
    res = rek.index_faces(
    CollectionId = 'smartdoor-visitors',
     Image={
        'Bytes' : buffer
        },
    ExternalImageId = name
    )
    return res

def getFaceId(fileName,name):
    s3 = boto3.client('s3')
    res = s3.get_object(
        Bucket = 'smartdoor-visitor-faces',
        Key = fileName
    )
    data = res['Body'].read()
    res = indexFaceRekognition(data,name)
    return res['FaceRecords'][0]['Face']['FaceId']

    
def lambda_handler(event, context):
    # TODO implement
    #faceId, name, phone, fileName = extractInformation(event)
    name, phone, fileName = extractInformation(event)
    faceId = getFaceId(fileName, name)
    table = connectToDB('visitors')
    putToDynamoDbVisitors(table,faceId,name,phone,fileName)
    table = connectToDB('passcodes')
    otp = putToDynamoDbPasscodes(table,faceId)
    sendSMS(phone,faceId,otp)
    message = "Thank you, visitor added to database"
    return {
        'statusCode': 200,
        'body': message
    }
