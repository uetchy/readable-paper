FROM python:3.6.5-onbuild

# install pandoc
RUN apt-get update && \
	apt-get install -y pandoc pandoc-citeproc

# avoid print() issue
# see http://stackoverflow.com/questions/27301468/how-do-i-display-output-from-python-application-running-inside-docker-container
ENV PYTHONUNBUFFERED 0

CMD ["rq",  "worker", "--url", "redis://redis:6379"]