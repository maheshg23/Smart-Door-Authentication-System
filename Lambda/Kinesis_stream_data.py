from __future__ import print_function
import json
import base64
import boto3
import cv2
import random
import uuid
from datetime import datetime


def sendSMS(faceId, phone, otp):
    sns = boto3.client('sns',region_name= 'us-east-1')
    url = "https://smartdoorauthentication.s3.amazonaws.com/OTPlogin.html?faceId="+faceId
    message = "Your OTP is - " + str(otp) + "\n\n click here to enter OTP " + url
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


def getVisitorsPhoneNumber(tableName,faceId):
    print("get_visitor_phone_number")
    item = tableName.get_item( 
        Key={'faceId': faceId
        })
    # print(json.dumps(item, indent=2))
    return item['Item']['phone']
    
    
def connectToDB(tableName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    print(table.creation_date_time)
    return table  


def sendEmail(url,fileName):
    visitorUrl = "http://smartdoorauthentication.s3-website-us-east-1.amazonaws.com/VisitorInfo.html?fileName="+fileName
    ses = boto3.client('ses')
    response = ses.send_email(	Destination={
        'ToAddresses': [
            'kp2492@nyu.edu',
            'maheshg@nyu.edu',
            ],
    },
    Message={
        'Body': {
            'Html': {
                'Charset': 'UTF-8',
                'Data': '<a class="ulink" href="'+url+'">Click here for Vistors photo</a>.<br><br>'+
                    '<a class= "ulink" href = "'+visitorUrl+'">Click here to enter information</a>',
            }
        },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': 'SmartDoor Email Lambda Function',
        },
    },
    Source='prashkar666@gmail.com' 
    )


def countNumberOfFrames(vidcap,fileName):
    total = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        total+=1
        if total > 500:
            break
    vidcap.release()
    vidcap.open(fileName)
    for i in range(1,int(total/2)):
        success, image = vidcap.read()
    return success,image


def getEndpoint(streamName):
    kvm = boto3.client("kinesisvideo")
    endpt = kvm.get_data_endpoint( 
        APIName = "GET_MEDIA_FOR_FRAGMENT_LIST",
        StreamName=streamName,
    )
    return endpt["DataEndpoint"]
    
def getImageFromFragments(endpoint, streamName, fragmentNumber):
    kvm = boto3.client('kinesis-video-archived-media',endpoint_url = endpoint)  
    response = kvm.get_media_for_fragment_list(
        StreamName=streamName,
        Fragments=[
            fragmentNumber,
        ]
    )
    print("FragmentNumber: "+fragmentNumber)
    
    mkvFileName = '/tmp/test.mkv'
    jpgFileName = '/tmp/frame.jpg'
    stream = response["Payload"]
    f = open(mkvFileName,'wb')
    f.write(stream.read())
    f.close()
    
    vidcap = cv2.VideoCapture(mkvFileName) 
    success,image = countNumberOfFrames(vidcap,mkvFileName)
    if success:
        cv2.imwrite(jpgFileName , image) #apparently we cannot see this file im lambda, check if uploaded to S3
    
    return jpgFileName

def uploadFileToS3Bucket(bucket, jpgFileName, identifier):
    # s3 = boto3.resource('s3')
    # s3.Bucket(bucket).upload_file(jpgFileName, fileName)
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        jpgFileName,        #filepath
        bucket,             #bucket Name
        'frame_{}.jpeg'.format(identifier),        #key 
    )


def getEmailDetails(bucket,identifier):
    fileName = "frame_"+identifier+".jpeg"
    url = "https://"+bucket+".s3.amazonaws.com/"+fileName
    return url,fileName


def getParametersFromKDS(event):
    for record in event['Records']:
        #Kinesis data is base64 encoded so decode here
        payload=base64.b64decode(record["kinesis"]["data"])
        print("Decoded payload: " + str(payload))
    
        json_data = json.loads(payload.decode('utf-8'))
        # print("Decoded json_data payload: " + str(json_data))
        face_search_response = json_data['FaceSearchResponse']
        
        # faceId = "f81b6fb6-f56a-4b32-b4b9-4b3b96ce4ee7"
        # return True, faceId , None
        
        if face_search_response:
            # return ("No one at the door")
            for faces in face_search_response:
                if faces['MatchedFaces']:
                    faceId = faces['MatchedFaces'][0]['Face']['FaceId']
                    print('FACEID ',faceId)
                    return True, faceId , None
                else:
                    fragmentNumber= json_data['InputInformation']['KinesisVideo']['FragmentNumber']
                    return True, None, fragmentNumber
        else:
            # fragmentNumber= json_data['InputInformation']['KinesisVideo']['FragmentNumber']
            # return False, None, fragmentNumber
            return False,None,None
            
def checkForDuplicates(passcodetable,faceId):
    
    try: 
        dynamodb = boto3.client('dynamodb')
        res = dynamodb.get_item(
            TableName = "passcodes",
            Key = {
                'faceID' : {
                    'S' : faceId
                }
            })
        timeStamp = res["Item"]["ExpirationTimeStamp"]["N"]
        curTimeStamp = int(datetime.now().timestamp())
        return curTimeStamp <= int(timeStamp)
    except KeyError:
        return False

def checkEmailDuplicate(emailTable, ownerEmailId):
    try:
        dynamodb = boto3.client('dynamodb')
        res = dynamodb.get_item(
            TableName = "emailFilter",
            Key = {
                'emailId' : {
                    'S' : ownerEmailId
                }
            })
            
        timeStamp = res["Item"]["ExpirationTimeStamp"]["N"]
        curTimeStamp = int(datetime.now().timestamp())
        return curTimeStamp <= int(timeStamp)
    except KeyError:
        return False
        
    
def putToDynamoDbEmailFilter(table, ownerEmailId):
    currenttimestamp = int(datetime.now().timestamp()) 
    table.put_item(
        Item={
            'emailId' : ownerEmailId,
            'ExpirationTimeStamp' : (currenttimestamp + 300),
            'CurrentTimeStamp' : currenttimestamp,
            })
    print("Added email to the email filter");
    return True
    
    
def lambda_handler(event, context):
    
    print(event)
    #if old face return faceId in parameter, otherwise return fragment number in parameter
    #success should be true if old face, false if new face
    success, faceId, fragmentNumber = getParametersFromKDS(event)  
    
    #fragmentNumber= json_data['InputInformation']['KinesisVideo']['FragmentNumber']
    # fragmentNumber = '91343852333181521524364891175229548375108484567'
    
    if success:
        if faceId is not None: 
            print("Valid Vistor")
            passcodetable = connectToDB("passcodes")
            if not checkForDuplicates(passcodetable,faceId):
                otp = putToDynamoDbPasscodes(passcodetable,faceId)
                vistiorsTable = connectToDB("visitors")
                phoneNumber = getVisitorsPhoneNumber(vistiorsTable,faceId)
                print("phone "+ phoneNumber)
                sendSMS(faceId, phoneNumber, otp)
            else:
                print("Duplicate Request for FaceId - " + faceId)
        
        elif fragmentNumber is not None: 
            print("Unknown Vistor")
            streamName="KVS1"
            bucket = "smartdoor-visitor-faces"
            identifier=str(uuid.uuid1())
            emailTable = connectToDB("emailFilter")
            print("uuid "+identifier)
            ownerEmailId = "maheshg@nyu.edu"
            if not checkEmailDuplicate(emailTable, ownerEmailId):
                endpoint = getEndpoint(streamName)
                jpgFileName = getImageFromFragments(endpoint, streamName, fragmentNumber)
                url, fileName = getEmailDetails(bucket, identifier)
                uploadFileToS3Bucket(bucket, jpgFileName, identifier)
                print("Send Email")
                # add data in emailfilter table
                putToDynamoDbEmailFilter(emailTable,ownerEmailId)
                sendEmail(url, fileName)
            else:
                print("Duplicate Email Request")
    else:
        print("Noone at the Door")
        return ("Noone at the Door")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
