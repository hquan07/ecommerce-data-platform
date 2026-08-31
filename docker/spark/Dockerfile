FROM bitnami/spark:3.5.0

USER root

# Install Python dependencies for PySpark
COPY requirements.txt /opt/bitnami/spark/requirements.txt
RUN pip install --no-cache-dir -r /opt/bitnami/spark/requirements.txt

USER 1001
