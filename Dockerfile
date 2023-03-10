# pull official base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y gettext libgettextpo-dev
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/bin

# run entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
