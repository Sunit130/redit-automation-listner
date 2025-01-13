# Use a Python base image
FROM public.ecr.aws/docker/library/python:3.10

# Set working directory
WORKDIR /app

# Update package list and install required packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    vim \
    && apt-get clean

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the application
CMD ["python", "main.py"]
