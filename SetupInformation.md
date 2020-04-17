# Setup Infromation for the Application

## GStreamer Plugin for  Mac 
Go to [2] and build you Gstreamer Plugin 

Go to the GStreamer Producer folder to start the Gstreamer
`cd amazon-kinesis-video-streams-producer-sdk-cpp/kinesis-video-native-build/downloads/local/bin`

Run the following Command to start the GStreamer to capture the video stream 

`gst-launch-1.0 -v avfvideosrc ! videoconvert ! vtenc_h264_hw allow-frame-reordering=FALSE realtime=TRUE max-keyframe-interval=45 ! kvssink name=sink stream-name="YOUR_KENISIS_STREAM_NAME" access-key="YOUR_ACCESS_KEY" secret-key="YOUR_SECRET_KEY" aws-region="us-east-1" osxaudiosrc ! audioconvert ! avenc_aac ! queue ! sink.`

## Setup AWS Rekognition 
run the commands in the rekog_aws_cli_commands.txt before you start the GStreamer stream

## OpenCV Library Build
We need to build our own openCV library which we can attach it to the Kinesis_stream_data lambda funtion using the lambda layers 
Refer to [5] create a zip files and add it to the Lambda Layer.

After you add the OpenCV Zip file into the lambda layer and then attach the layer to the lambda function we need to change the envionemnt variable 

PYTHONPATH = /var/runtime:/opt/

/var/runtime -> is for Boto3 and other python libraries 
/opt/ -> is for the OpenCV library that we added to the Lambda layer 

## DynamoDB Tables 
Create 3 DynamoDB Tables - visitors, passcode and emailfilter


## Reference - 
[1] https://medium.com/@matt.collins/facial-recognition-with-a-raspberry-pi-and-kinesis-video-streams-part-2-9c9a631e8c24  
[2] https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp/blob/master/README.md  
[3] https://medium.com/faun/a-quick-introduction-to-aws-rekognition-8257d4777198  
[4] https://github.com/aeddi/aws-lambda-python-opencv/blob/master/build.sh  
[5] https://itnext.io/create-a-highly-scalable-image-processing-service-on-aws-lambda-and-api-gateway-in-10-minutes-7cbb2893a479  
