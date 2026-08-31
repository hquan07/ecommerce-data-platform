FROM apache/spark:3.5.0

USER root

# Install Python dependencies for PySpark
COPY requirements.txt /opt/spark/work-dir/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/spark/work-dir/requirements.txt

USER 185
