FROM python:3.6.0-onbuild

# install pandoc
RUN apt-get update && \
	  apt-get install -y pandoc pandoc-citeproc

# avoid print() issue
# see http://stackoverflow.com/questions/27301468/how-do-i-display-output-from-python-application-running-inside-docker-container
ENV PYTHONUNBUFFERED 0

# expose web port
EXPOSE 80

CMD ["python", "app.py"]