FROM ubuntu:18.04

MAINTAINER Yudong Lee <leeyudon@amazon.com>

RUN apt-get -y update && apt-get install -y --no-install-recommends --reinstall build-essential\
         wget \
         make \
         gcc \
         python3-pip \
         python3-dev \
         python3-setuptools \
         git \
         nginx \
         ca-certificates \
         software-properties-common \
    && rm -rf /var/lib/apt/lists/*
    # && python -v
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN pip install --upgrade pip \
    && pip install scipy==1.2.2 awscli sagemaker sagemaker-containers 
    
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/ml/code:${PATH}"

COPY check_status.py /opt/ml/code/check_status.py