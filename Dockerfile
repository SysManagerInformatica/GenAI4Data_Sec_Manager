# ================================================================================
#   GenAI4Data Security Manager
#   Module: Docker Container Configuration
# ================================================================================
#   Version:      2.0.0
#   Release Date: 2024-12-15
#   Author:       Lucas Carvalhal - Sys Manager
#   Company:      Sys Manager Informática
#   
#   Description:
#   Docker container configuration for deploying GenAI4Data Security Manager
#   on Google Cloud Run with Python 3.12 runtime environment.
# ================================================================================

#Base Image to use
FROM python:3.12
EXPOSE 8080
WORKDIR /genai4datasec
COPY . ./
#install all requirements in requirements.txt
RUN pip install -r requirements.txt
# Run the web service on container startup
CMD ["python3", "main.py"]
