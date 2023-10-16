# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project dependencies
RUN pip install poetry && \
    poetry install --no-root --no-dev

# Copy the rest of your application code to the container
COPY auto_post_classifier /app

# Specify the command to run your application
CMD ["poetry", "run", "main.py"]
