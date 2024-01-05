# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

COPY . .

# Install Poetry and project dependencies
RUN pip install poetry && \
    poetry install --only main

# # Specify the command to run your application
CMD ["./entrypoint.sh"]
