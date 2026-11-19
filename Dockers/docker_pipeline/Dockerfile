FROM python:3.12-slim
#setting a folder inside the container as the work dir:
WORKDIR /app

#requiremnts for pipeline
COPY reqirments.txt .
RUN pip install --no-cache-dir -r reqirments.txt

#copy the files in the local folder to put into the work dir
COPY . /app
#when the container starts, i want it to do this
ENTRYPOINT ["python3", "app.py"]