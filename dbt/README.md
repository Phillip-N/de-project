## dbt Setup

The below setup instructions are taken from the main project README found here: https://github.com/Phillip-N/de-project#readme

### dbt Transformations
After running the etl deployment from prefect UI, the required parquet files should be uploaded to your GCS bucket, and a dataset and two tables for used cars data should have been created in bigquery (canadian data and us data). You can now move on to deploying the dbt models.

1. Create a dbt account if you dont already have one, set up a project and establish a bigquery connection
2. Create a github repo based on the files in the dbt folder
3. Change the database name (deft-crawler-378422) in the models > staging > schema.yaml file to the name of your database.
4. Connect the repo to dbt
5. Run dbt build
