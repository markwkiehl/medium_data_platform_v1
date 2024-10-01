# syntax=docker/dockerfile:1

# slim version of Python 3.12 to minimize the size of the container and make it as lightweight as possible
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Optimize pip
ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
#ENV VAR="VALUE"


# set the default executable for a container 
ENTRYPOINT [ "python3" ]

# Define the command to run your Python script
CMD ["gcp_data_platform_sub.py"]

