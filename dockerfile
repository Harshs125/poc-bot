# Use the official Python base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app/backend_sakon

# Copy the Pipenv files
COPY Pipfile Pipfile.lock /app/backend_sakon/

# Install dependencies
RUN pip install pipenv && pipenv install --system

# Copy the Django project code
COPY . /app/backend_sakon/

# Expose the Django development server port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
