#!/bin/bash

# Variables
IMAGE_NAME="my-docker-image"
TAG="v1.0"
REGISTRY_URI="742352046111.dkr.ecr.us-east-1.amazonaws.com"
REPOSITORY_NAME="<repository_name>"
LAMBDA_FUNCTION_NAME="<lambda_function_name>"

# Login to Amazon ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin $REGISTRY_URI

# Build Docker Image
docker build -t $IMAGE_NAME:$TAG .

# Tag the Docker Image
docker tag $IMAGE_NAME:$TAG $REGISTRY_URI/$REPOSITORY_NAME:$TAG

# Push Docker Image to Amazon ECR
docker push $REGISTRY_URI/$REPOSITORY_NAME:$TAG

# Create AWS Lambda Function
aws lambda create-function --function-name $LAMBDA_FUNCTION_NAME \
--handler <handler_name> \
--runtime <runtime> \
--memory <memory_size> \
--timeout <timeout_in_seconds> \
--role <role_arn> \
--environment Variables="{<environment_variables>}" \

# Update AWS Lambda Function with Docker Image
aws lambda update-function-configuration --function-name $LAMBDA_FUNCTION_NAME \
--image-uri $REGISTRY_URI/$REPOSITORY_NAME:$TAG

