#!/bin/bash
rm my_dep.zip

# cd into package directory, and zip everything in there to ../my_dep.zip
cd package
zip -r ../my_dep.zip .
cd ..
zip my_dep.zip app.py

# Then, upload it to AWS Lambda
aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:742352046111:function:testFunction --zip-file fileb://my_dep.zip

