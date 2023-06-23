# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Create the backup_data folder
RUN mkdir -p /app/backup_data

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the environment variables (if needed)
ENV ENV_VARIABLE_NAME=value

# Start the Flask application
CMD ["python", "app.py"]
