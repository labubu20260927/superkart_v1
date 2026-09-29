# Slim Python base image keeps the container small
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Copy the requirements first so Docker can cache the dependency layer between builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# Port the API listens on
EXPOSE 7860

# Serve the Flask app with gunicorn:
#   -w 2             -> two worker processes
#   -b 0.0.0.0:7860  -> listen on all interfaces so the port can be published / forwarded
#   app:superkart_api -> <python file>:<Flask object>
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
