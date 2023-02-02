#!/bin/bash

# Variables
IMAGE_NAME="my-docker-image"
TAG="v1.0"
REGISTRY_URI="742352046111.dkr.ecr.us-east-1.amazonaws.com"
REPOSITORY_NAME="lambda-repository"
LAMBDA_FUNCTION_NAME="lambda-docker-function"

# Login to Amazon ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REGISTRY_URI

# Build Docker Image
docker build -t $IMAGE_NAME:$TAG .

# Tag the Docker Image
docker tag $IMAGE_NAME:$TAG $REGISTRY_URI/$REPOSITORY_NAME:$TAG

# Push Docker Image to Amazon ECR
docker push $REGISTRY_URI/$REPOSITORY_NAME:$TAG

# Create AWS Lambda Function
aws lambda create-function --function-name $LAMBDA_FUNCTION_NAME \
--handler "app.handler" \
--runtime "python3.8" \
--memory "1024MB" \
--timeout "5000" \
--role "arn:aws:iam::742352046111:role/service-role/myTestRole" 

# Update AWS Lambda Function with Docker Image
aws lambda update-function-configuration --function-name $LAMBDA_FUNCTION_NAME \
--image-uri $REGISTRY_URI/$REPOSITORY_NAME:$TAG