# netlify-functions/fastapi.py
import os
import sys
from fastapi import FastAPI
from mangum import Mangum

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  # Import the FastAPI app from your main.py file

handler = Mangum(app)  # Create a Mangum handler for AWS Lambda compatibility

def lambda_handler(event, context):
    return handler(event, context)
