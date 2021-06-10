FROM python:3.8
MAINTAINER Riana Valenzuela "rianav@uoregon.edu"
COPY . /website
WORKDIR /website
RUN pip install -r requirements.txt
CMD ["python", "website.py"]
