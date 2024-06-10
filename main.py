from fastapi import FastAPI, File, UploadFile, HTTPException
from google.cloud import storage, aiplatform
from vertexai.generative_models import GenerativeModel, Part
from dotenv import load_dotenv
import os
import uuid
import json

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

aiplatform.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()

storage_client = storage.Client()

def upload_image_to_gcs(file: UploadFile):

    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"images/{uuid.uuid4()}.png")
    print(f"GCS_BUCKET_NAME: {GCS_BUCKET_NAME}")

    try:
        # Upload the file to the blob
        blob.upload_from_file(file.file, content_type=file.content_type)
        # Construct the GS URL
        gs_url = f"gs://{GCS_BUCKET_NAME}/{blob.name}"
        print(f"File {file.filename} uploaded successfully to {GCS_BUCKET_NAME}.")
        print(f"GS URL: {gs_url}")
        return gs_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def process_image_with_vertex_ai(image_url):
    model = GenerativeModel(model_name="gemini-1.5-flash-001")
    response = model.generate_content(
        [
            Part.from_uri(
                image_url,
                mime_type="image/jpeg",
            ),
            '''
                Read this receipt fully. The image may not too good, but try to guess if it may be an ULTRA product and fill in the missing characters, ULTRA products will start with 'ULTRA' and it is often milk. Afterwards return the receipt details in this format:
                {
                    "merchant_address": "JLN Siradj Salman Rt:22",
                    "merchant_name": "AMINMAR",
                    "receipt_date": "2024-05-27",
                    "receipt_time": "13:03:05",
                    "receipt_number": "270520240192",
                    "total_filtered_amount": 25500,
                    "total_amount": 25500,
                    "items": [
                        {
                            "item_each_price": 5100,
                            "item_name": "ULTRA PLAIN 200 ML",
                            "item_quantity": 2000,
                            "item_quantity_unit": "PCS",
                            "item_total_price": 10200
                        },
                        {
                            "item_each_price": 5100,
                            "item_name": "ULTRA MOCCA 200 ML",
                            "item_quantity": 1000,
                            "item_quantity_unit": "PCS",
                            "item_total_price": 5100
                        },
                        {
                            "item_each_price": 5100,
                            "item_name": "ULTRA STRAW SLM 200 ML",
                            "item_quantity": 2000,
                            "item_quantity_unit": "PCS",
                            "item_total_price": 10200
                        }
                    ],
                    "store_code": ""
                    
                }
            '''
        ]
    )
    return response.text

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    try:
        image_url = upload_image_to_gcs(file)
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to S3")

        response = process_image_with_vertex_ai(image_url)

        clean_json_str = response.strip('```json\n').strip('\n```')

        receipt_json = json.loads(clean_json_str)

        result = {
            "status": "SUCCESS",
            "reason": "File Successfully Read",
            "read": receipt_json
            }
        return result
    except Exception as e:
        return {
            "status": "FAILED", 
            "reason": str(e), 
            "read": None
            }

@app.get("/list-gcs-bucket/")
def list_gcs_bucket_contents():
    """List contents of the GCS bucket"""
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blobs = bucket.list_blobs()
        return {"contents": [blob.name for blob in blobs]}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
