import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def validateOTP(res,userOtp):
    try:
        if res["Item"] is None:
            message = "invalid OTP"
        else:
            print(res["Item"])
            dbOTP = res["Item"]["OTP"]["N"]
            timeStamp = res["Item"]["ExpirationTimeStamp"]["N"]
            curTimeStamp = int(datetime.now().timestamp())
            userOtp = int(userOtp)
            dbOTP = int(dbOTP)
            timeStamp = int(timeStamp)
            if userOtp == dbOTP and timeStamp > curTimeStamp:
                message = "ACCESS GRANTED"
            else:
                message = "ACCESS DENIED"
                logger.debug("db - " + str(timeStamp) + " now - " + str(curTimeStamp))
                logger.debug("db - " + str(dbOTP) + " user - " + str(userOtp))
    except KeyError:
        message = "Invalid OTP"
    return message


def queryPasscodesDb(otp, faceId):
    dynamodb = boto3.client('dynamodb')
    res = dynamodb.get_item(
        TableName = "passcodes",
        Key = {
            'faceID' : {
                'S' : faceId
            }
        }
        )
    return res


def extractAttributes(res):
    return res["otp"],res["faceId"]
    

def lambda_handler(event, context):
    logger.debug("Helloo")
    otp, faceId = extractAttributes(event["message"])
    res = queryPasscodesDb(otp,faceId)
    logger.debug("here")
    message = validateOTP(res,otp)
    
    return {
        'statusCode': 200,
        'body': message
    }
