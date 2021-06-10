FROM python:3.8
LABEL maintainer="rianav@uoregon.edu"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "flask_brevets.py"]
