from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from datetime import timedelta
from google.cloud import bigquery
import os
from kaggle_build import build_kaggle_json
import zipfile

@task(retries=3, log_prints=True)
def fetch_dataset() -> pd.DataFrame:
    # Builds kaggle file based on env variables passed on docker run
    build_kaggle_json()
    
    import kaggle
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files('rupeshraundal/marketcheck-automotive-data-us-canada', 'marketcheck-automotive-data-us-canada', quiet=False, unzip=False, force=True)

    with zipfile.ZipFile("./marketcheck-automotive-data-us-canada/marketcheck-automotive-data-us-canada.zip", "r") as zip_ref:
        for name in zip_ref.namelist():
            try:
                zip_ref.extract(name, "marketcheck-automotive-data-us-canada/")
            except OSError as e:
                print(e)
                pass

    can_df = pd.read_csv('marketcheck-automotive-data-us-canada/ca-dealers-used.csv')
    us_df = pd.read_csv('marketcheck-automotive-data-us-canada/us-dealers-used.csv')

    return can_df, us_df

@task(log_prints=True)
def clean(df) -> pd.DataFrame:
    """Fix dtype issues"""
    df.dropna(axis=0, subset=['year'], inplace=True)
    df['year'] = df['year'].astype(int)
    df['zip'] = df['zip'].astype(str)

    return df

@task(log_prints=True)
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write Dataframe out locally as a parquet file"""
    # Uncomment this if you chose to run locally
    # if os.path.exists(Path("data/")):
    #     pass
    # else:
    #     os.makedirs(Path("data/"))
    
    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path, index=False)
    return path

@task(log_prints=True)
def write_gcs(path: Path) -> None:
    "Upload local parquet file to GCS"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path = f"{path}",to_path = path.as_posix())
 
@task()
def create_bq_dataset():
    """Creates dataset"""
    dataset_id = "{}.used_cars_data".format(client.project)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "europe-west6"

    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))


@task(log_prints=True)
def write_bq(table_name, file_name):
    """Write GCS to BigQuery"""
    table_id = f"deft-crawler-378422.used_cars_data.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
    )

    uri = f"gs://dtc_data_lake_deft-crawler-378422/data/{file_name}.parquet"
    
    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table = client.get_table(table_id)
    print("Loaded {} rows.".format(destination_table.num_rows))

@flow()
def etl_web_to_gcs(can_file, us_file) -> None:
    """The main ETL function"""
    can_df, us_df = fetch_dataset()

    clean(can_df)
    clean(us_df)
    path_can = write_local(can_df, can_file)
    path_us = write_local(us_df, us_file)
    write_gcs(path_can)
    write_gcs(path_us)

@flow()
def etl_gcs_to_bq(file_name, table_name):
    """Main ETL flow to load data into Big Query"""
    write_bq(file_name, table_name)

@flow()
def etl_parent_flow(can_file, us_file):
    etl_web_to_gcs(can_file, us_file)
    
    create_bq_dataset()
    etl_gcs_to_bq("canada_used_cars", can_file )
    etl_gcs_to_bq("usa_used_cars", us_file)

if __name__ == "__main__":
    client = bigquery.Client()
    etl_parent_flow("ca-dealers-used", "us-dealers-used")