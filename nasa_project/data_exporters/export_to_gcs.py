from google.oauth2 import service_account
from google.cloud import storage
import json
import os
import io

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_google_cloud_storage(df, **kwargs):
    # --- Credentials handling ---
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    with open(creds_path, 'r', encoding='utf-8') as f:
        creds_dict = json.load(f)

    # Sanitize private_key to prevent formatting issues
    creds_dict['private_key'] = (
        creds_dict['private_key']
        .replace('\r\n', '\n')
        .replace('\r', '\n')
    )

    # Authentication using sanitized credentials
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = storage.Client(credentials=credentials)

    # --- GCS Configuration ---
    bucket_name = 'autonomous-star-461514-d8-nasa'
    object_key = 'asteroids_data.parquet'

    # --- Buffer and Parquet export ---
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    # --- Data upload ---
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_key)
    blob.upload_from_file(buffer, content_type='application/octet-stream')

    print(f'✅ Upload complete: gs://{bucket_name}/{object_key}')
    
    # Return dataframe for downstream blocks
    return df