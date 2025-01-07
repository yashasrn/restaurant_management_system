# Use Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
