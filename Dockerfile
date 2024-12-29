# Use an official Python runtime as a base image
FROM python:3.10-slim
# Set the working directory inside the container
WORKDIR /app
# Copy requirements file 
COPY requirements.txt requirements.txt
# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the current directory contents into the container
COPY . /app/
# Expose the port that Django will run on (default is 8000)
EXPOSE 8000
# Set the environment variable to tell Django not to run in debug mode in production
ENV PYTHONUNBUFFERED 1
# Copy the entrypoint.sh script into the container
COPY entrypoint.sh /entrypoint.sh
COPY cron-entrypoint.sh /cron-entrypoint.sh
# Give the script executable permissions
RUN chmod +x /entrypoint.sh
RUN chmod +x /cron-entrypoint.sh
