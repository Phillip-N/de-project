FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .
# COPY kaggle.json .

RUN pip install -r docker-requirements.txt --trusted-host pypi.python.org --no-cache-dir

RUN mkdir -p /opt/prefect/data/
RUN mkdir -p /opt/prefect/flows/

COPY kaggle_build.py /opt/prefect/flows/kaggle_build.py
COPY ingest_flow.py /opt/prefect/flows/ingest_flow.py
# COPY data /opt/prefect/data