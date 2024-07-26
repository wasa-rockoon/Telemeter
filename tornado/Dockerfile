# Use an official Python runtime as a parent image
FROM python:3

# Change working directory
WORKDIR /app

# Copy the current directory contents into the container at /telemeter_api
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Run commands when the container launches
CMD ["python3", "-u", "app.py"]

