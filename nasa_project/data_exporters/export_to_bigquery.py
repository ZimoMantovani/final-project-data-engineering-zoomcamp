import pandas as pd
import json
import os
from google.oauth2 import service_account
from google.cloud import bigquery

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_bigquery(df, **kwargs) -> None:
    # --- Data validation ---
    if isinstance(df, list):
        df = pd.DataFrame(df)
        
    if df.empty:
        raise ValueError("❌ DataFrame is empty. Please check the upstream extraction block.")

    # --- Credentials handling ---
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '/home/src/credentials/gcp-service-account.json')

    with open(creds_path, 'r', encoding='utf-8') as f:
        creds_dict = json.load(f)

    # Fix for RSA private key formatting issues
    creds_dict['private_key'] = (
        creds_dict['private_key']
        .replace('\r\n', '\n')
        .replace('\r', '\n')
    )

    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # --- BigQuery client initialization ---
    project_id = creds_dict['project_id']
    client = bigquery.Client(credentials=credentials, project=project_id)

    # --- Schema enforcement ---
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
    if 'close_approach_date' in df.columns:
        df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    else:
        raise KeyError("❌ 'close_approach_date' column is missing; required for partitioning.")

    if 'is_potentially_hazardous' in df.columns:
        df['is_potentially_hazardous'] = df['is_potentially_hazardous'].astype(bool)

    # --- Load configuration: Partitioning & Clustering ---
    table_id = f"{project_id}.nasa_neo_data.asteroids_raw"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE", 
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="close_approach_date",  
        ),
        clustering_fields=["is_potentially_hazardous"] 
    )

    # --- Data ingestion ---
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  

    print(f"✅ Data successfully loaded to BigQuery!")
    print(f"📌 Table: {table_id}")
    print(f"📊 Partitioned by: close_approach_date | Clustered by: is_potentially_hazardous")