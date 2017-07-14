FROM continuumio/anaconda3:latest

MAINTAINER Osman Baskaya <osbaskaya@gmail.com>

RUN apt-get install -y vim
RUN pip install -r requirements.txt
