FROM public.ecr.aws/lambda/python:3.9

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}/
COPY ./agents/ ${LAMBDA_TASK_ROOT}/agents/
COPY ./chirpy/ ${LAMBDA_TASK_ROOT}/chirpy/
COPY ./servers/ ${LAMBDA_TASK_ROOT}/servers/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
