# Slim Python base image keeps the container small
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Copy the requirements first so Docker can cache the dependency layer between builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app
COPY . .

# Default backend address = name of the backend container on the shared Docker network
ENV BACKEND_URL=http://superkart-backend:7860

# Port the Streamlit app listens on
EXPOSE 8501

# Start Streamlit:
#   --server.address=0.0.0.0           -> reachable from outside the container (port forwarding)
#   --server.enableCORS / XsrfProtection=false -> needed behind the Codespaces forwarding proxy (file upload)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
