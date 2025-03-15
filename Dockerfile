# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.10-slim
# Set environment variables
ENV PYTHONUNBUFFERED 1
# Set the working directory
WORKDIR /app
# Install dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
# Copy application code
COPY . /app/
# Expose the port the app runs on
EXPOSE 8080
# Command to run the app
CMD ["python", "-m", "chainlit", "run", "app.py", "-h", "--port", "8080"]