# Smart-Door-Authentication-System
##### [Link To Web Application](http://restaurant-chatbot.s3-website-us-east-1.amazonaws.com/)


## FRONTEND (HTML, JavaScript, CSS)
The frontend is hosted in AWS S3 and provides a web-app user interface to interact with the chat bot. Many open source libraries and frameworks were used to design the UI/UX of the bot. 

## DESCRIPTION
"Smart-Door-Authentication-System" is a serverless, microservice driven web-based application. It builds a distributed system that authenticates people and provides them with access to a virtual door. It is designed using multiple AWS components such as:-
##### AWS Kinesis, Rekognition, Kinesis Data Stream, S3-Buckets, API-Gateway, Swagger, Lambda Functions, Cognito, DynamoDB, SNS, SES, Cloud Watch.

This is a door authentication system that will scan a person at the door using AWS Kinesis Video Streams and AWS Rekognition and provide an OTP passcode to the User using which the person can enter the door. 

## ARCHITECHTURE :- 
![alt text](https://github.com/maheshg23/Smart-Door-Authentication-System/blob/master/images/Architecture.png)


## SAMPLE UI OF THE WEB APPLICATION
![alt text](https://github.com/maheshg23/Smart-Door-Authentication-System/blob/master/images/ApplicationUI.jpg)


## SAMPLE OUTPUT 
### Known Visitor 
The person at the door recieves an SMS of the OTP which is valid only for 5 minutes :- 
![alt text](https://github.com/maheshg23/Smart-Door-Authentication-System/blob/master/images/KnownVisitor.jpeg)

### Unknown Visitor
The Owner recieves an Email with the persons image and a link to add the Unknown vistitor to the database.
![alt text](https://github.com/maheshg23/Smart-Door-Authentication-System/blob/master/images/UnKnownVisitor.png)
 


