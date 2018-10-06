# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
# FROM python:alpine
FROM python:3.6.5-onbuild

# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=readable-paper Version=0.0.1
EXPOSE 3000

# avoid print() issue
# see http://stackoverflow.com/questions/27301468/how-do-i-display-output-from-python-application-running-inside-docker-container
ENV PYTHONUNBUFFERED 0

WORKDIR /app
ADD . /app

# Using pip:
RUN python3 -m pip install -r requirements.txt
# CMD ["python3", "-m", "readable-paper"]
CMD ["python3", "app.py"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "readable-paper"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m readable-paper"
