FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container's working directory
COPY . .

# Install the dependencies without caching, to keep the image small
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start the application with Gunicorn
# -w 4                : four worker processes
# -b 0.0.0.0:7860     : bind to port 7860 on all network interfaces
# app:superkart_api   : module app.py, Flask instance superkart_api
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
