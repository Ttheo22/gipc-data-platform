FROM public.ecr.aws/lambda/python:3.12

# Copy dependency list and install
COPY requirements-lambda.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements-lambda.txt --target "${LAMBDA_TASK_ROOT}"

# Copy your application code
COPY handler.py ${LAMBDA_TASK_ROOT}
COPY extractors/ ${LAMBDA_TASK_ROOT}/extractors/
COPY transformers/ ${LAMBDA_TASK_ROOT}/transformers/
COPY loaders/ ${LAMBDA_TASK_ROOT}/loaders/

# Set the Lambda entry point: filename.function_name
CMD [ "handler.lambda_handler" ]