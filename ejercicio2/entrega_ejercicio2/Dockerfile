# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ ./src/
COPY sales/ ./sales/
COPY tests/ ./tests/

# Create the reports directory
RUN mkdir -p /app/reports

# Set the command to run the application
CMD ["python", "src/sales_analyzer.py"]
