FROM continuumio/anaconda3

MAINTAINER Osman Baskaya <osbaskaya@gmail.com>

RUN apt-get update && apt-get install -y --no-install-recommends make automake gcc build-essential g++ cpp libc6-dev man-db autoconf pkg-config
RUN apt-get -y install vim git libfreetype6-dev libxft-dev gcc g++

RUN git clone https://github.com/osmanbaskaya/coarse-wsd.git

WORKDIR /coarse-wsd

RUN git checkout develop-py3

RUN conda create --yes --name coarse-wsd-py3 python=3.6
RUN source activate coarse-wsd-py3

RUN pip install -r requirements.txt

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]
