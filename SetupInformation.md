## GStreamer Plugin Mac 
Go to https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp/blob/master/README.md and build you Gstreamer Plugin 

Go to the GStreamer Producer folder to start the Gstreamer
cd amazon-kinesis-video-streams-producer-sdk-cpp/kinesis-video-native-build/downloads/local/bin

Run the following Command to start the GStreamer to capture the video stream 

gst-launch-1.0 -v avfvideosrc ! videoconvert ! vtenc_h264_hw allow-frame-reordering=FALSE realtime=TRUE max-keyframe-interval=45 ! kvssink name=sink stream-name="KVS1" access-key="AKIARWH2FUSZVMOSWQUG" secret-key="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" aws-region="us-east-1" osxaudiosrc ! audioconvert ! avenc_aac ! queue ! sink.

## To setup Rekognition 
run the commands in the rekog_aws_cli_commands.txt before you start the GStreamer stream

## OPENCV Library Build
We need to build our own openCV library which we can attach it to the Kinesis_stream_data lambda funtion using the lambda layers 
Refer this to create a zip files and add it to the Lambda Layer https://itnext.io/create-a-highly-scalable-image-processing-service-on-aws-lambda-and-api-gateway-in-10-minutes-7cbb2893a479

After you add the OpenCV Zip file into the lambda layer and then attach the layer to the lambda function we need to change the envionemnt variable 

PYTHONPATH = /var/runtime:/opt/

/var/runtime -> is for Boto3 and other python libraries 
/opt/ -> is for the OpenCV library that we added to the Lambda layer 

## DynamoDB Tables 
Create 3 DynamoDB Tables - visitors, passcode and emailfilter
