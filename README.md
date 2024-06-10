
# Ultramilk Receipt Processing API

This project is a FastAPI-based web application that allows you to upload receipt images, processes them using Google Cloud Storage and Vertex AI, and returns structured receipt details in JSON format.

## Features

- **Image Upload**: Upload receipt images to Google Cloud Storage.
- **Image Processing**: Process uploaded images using Vertex AI to extract receipt details.
- **List Bucket Contents**: List the contents of the Google Cloud Storage bucket.

## Requirements

- Python 3.7+
- Google Cloud SDK
- FastAPI
- Uvicorn
- `python-dotenv`
- `google-cloud-storage`
- `vertexai`
- Service account with the necessary permissions

## Setup

1. **Clone the Repository**:

    ```bash
    git clone https://your-repository-url.git
    cd your-repository-directory
    ```

2. **Create and Activate a Virtual Environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
   
   Create a `.env` file in the root of the project with the following content:

    ```env
    GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-file.json
    PROJECT_ID=your-google-cloud-project-id
    LOCATION=your-vertex-ai-location
    GCS_BUCKET_NAME=your-gcs-bucket-name
    ```

5. **Run the Application**:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## Usage

### Endpoint to Process Image

- **URL**: `/process-image/`
- **Method**: POST
- **Description**: Uploads an image to GCS and processes it with Vertex AI.
- **Request**:
    - **file**: The image file to be uploaded and processed.

- **Response**:
    - **status**: "SUCCESS" if the file was successfully read, otherwise "FAILED".
    - **reason**: Detailed message.
    - **read**: The extracted receipt details in JSON format.

### Endpoint to List GCS Bucket Contents

- **URL**: `/list-gcs-bucket/`
- **Method**: GET
- **Description**: Lists the contents of the specified GCS bucket.
- **Response**:
    - **contents**: A list of objects in the GCS bucket.
    - **error**: Error message, if any.

## Example

### Process an Image

Use `curl` to upload an image and process it:

```bash
curl -X POST "http://127.0.0.1:8000/process-image/" -F "file=@/path/to/your/image.png"
