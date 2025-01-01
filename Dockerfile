# Use Python base image
FROM python:3.9
# main working directory in the container
WORKDIR /app
# copy main application files into container 
COPY . /app
# install dependencies from requirements.txt
RUN pip install -r requirements.txt
# the port on which app will run 
EXPOSE 5000
# Command to run application
CMD ["python", "app.py"]

