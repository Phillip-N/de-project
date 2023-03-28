# de-project

## Table of contents
1. [Purpose of the Project](#purpose)
2. [Data Pipeline Architecture](#architecture)
3. [Project Prerequisites](#prereq)
4. [Steps to Reproduce](#repro)
    * [Getting Started](#gs)
    * [Docker Data Ingestion](#ddi)
    * [dbt Transformations](#dt)
5. [Project Details](#pd)
    * [Data Ingestion](#pd-di)
    * [dbt Transformations](#pd-dt)
    * [Analytics](#pd-a)

## Purpose of the Project <a name='purpose'></a>
The purpose of the project is build a data pipeline using the skills learned from the Data Engineering Zoomcamp (https://github.com/DataTalksClub/data-engineering-zoomcamp). 

## Data Pipeline Architecture <a name='architecture'></a>
The pipeline architecture can be seen in the below diagram. Technologies that will be used include:
* Prefect
* Docker
* Google Cloud Platform (GCS, Bigquery)
* dbt
* Looker Studios

![image](https://user-images.githubusercontent.com/10274304/228389951-c7e79540-7e68-4d74-a2a2-dda0399cb1d7.png)

## Project Prerequisites <a name='prereq'></a>
Although the project is designed to be easily reproducible, there are a few prerequisites that should be noted.
1. Have a google cloud account and a project already set up.
2. Have completed the GCP initial setup done in week 1 of the data engineering zoomcamp (created a GCS bucket, create a service account, download the credentials, download and setup google SDK and assign the environmental variable for GOOGLE_APPLICATION_CREDENTIALS.
3. Have a Kaggle account and create an API token https://www.kaggle.com/docs/api
4. Have a dbt account
5. Have a dockerhub account and docker installed and set up on your computer
6. Have prefect installed and setup on your computer (we will be using the local version because its free)

## Steps to Reproduce <a name='repro'></a>

### Getting Started <a name='gs'></a>
Before you start, you need to create two blocks on prefect, one for docker, and one for GCS. The docker block name needs to be updated in the docker_deploy.py file and the gcs block name needs to be updated in the write_gcs function in the ingest_flow.py module. You will also need to update "deft-crawler-378422" in the ingest_flow.py file to your google cloud project name, and dataset.location = "europe-west6" to whatever location your project is set to.

### Docker Data Ingestion <a name='ddi'></a>
1. Save down your kaggle.json file in the same directory as the ingest_flow.py script
2. Build your docker image using `docker image build --no-cache -t {dockerhub_account}/{repo_name}:cars-data-ingest .`
3. Push your docker image using `docker image push {dockerhub_account}/{repo_name}:cars-data-ingest`
4. Start your prefect orion server with `prefect orion start`
5. Start your prefect agent with `prefect start -q default`
6. Run docker deploy to create the deployment on prefect `python docker_deploy.py'
7. Run the deployment through prefect `prefect deployment run etl-parent-flow/docker-flow`

### dbt Transformations <a name='dt'></a>
After running the deployment in the previous step, the required parquet files should be uploaded to your GCS bucket, and a dataset and two tables for used cars data should have been created in bigquery (canadian data and us data). You can now move on to deploying the dbt models.

1. Create a dbt account if you dont already have one, set up a project and establish a bigquery connection
2. Create a github repo based on the files in the dbt folder
3. Change the database name (deft-crawler-378422) in the models > staging > schema.yaml file to the name of your database.
4. Connect the repo to dbt
5. Run `dbt build`

## Project Details <a name='pd'></a>

### Data Ingestion <a name='pd-di'></a>
Data ingestion was done using python, Prefect, and the google cloud API. The data itself came from kaggle.com and can be found here: https://www.kaggle.com/datasets/rupeshraundal/marketcheck-automotive-data-us-canada. The ingestion script was dockerized for ease of repoducibility. Transformations at this stage were kept to a minimal to preserve the data integrity within the data lake and because there were no complex transformations that couldn't be otherwise done in dbt.

Thoughts:
* In a live production environment, with data coming in daily, it would make sense to use Prefect cloud and have scheduled deployments to update the GCS buckets, and bq tables.
* Due to the low level of complexity of the dataset, using spark was not necessary, especially when we only have historical data and the transforms operations are mainly trivial.

### dbt Transformations <a name='pd-dt'></a>
dbt was used to transform and prepare the data so that it can be later analyzed. Since the ingestion script took care of uploading the data to GCS and building bq tables, we simply need to conduct on transformations on the data that already exists in bq. Models were created to alter datatypes, combine the two datasets into a single table, and create a new table that measures average mileage utilization and average price metrics. Tests were also created to ensure uniqueness and non null across certain fields. Documentation is based off of marketchecks car data dictionary:  https://storage.googleapis.com/marketcheck-sample-feeds/cars_data_dictionary.xlsx.

Thoughts:
* Data freshness would be a consideration in a production environment with data coming in daily.
* dbt job scheduling would also be a consideration in production.

The dbt lineage can be seen below:
![image](https://user-images.githubusercontent.com/10274304/228389140-8a661d05-b2a5-4793-a5a4-ad9415dd045a.png)

### Analytics <a name='pd-a'></a>
Analytics was done using looker studios. Since we already have data in bigquery through our dbt transformations, setting up a connection to the bq data source was quick simple. The looker dashboard itself pulls data from two sources, the total inventory table (combining us and can data) and the business metrics table - both of which were created through dbt. Link to the dashboard: https://lookerstudio.google.com/reporting/5d403386-9e78-4c5d-bb45-083e7e98b028/page/5oXKD

A preview of the dashboard can also be seen below:

![image](https://user-images.githubusercontent.com/10274304/228389687-29e2faa8-e63b-4158-8e59-66335f413326.png)





