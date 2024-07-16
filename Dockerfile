FROM python:3.12.4-slim

# Set the working directory
WORKDIR /app

# Copy your application code to the container
COPY . /app

# Install dependencies (assuming you have a requirements.txt)
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 8002

# Command to run when container starts
CMD ["uvicorn", "main:app", "--reload", "--port=8002", "--host=0.0.0.0", "--lifespan", "off"]
