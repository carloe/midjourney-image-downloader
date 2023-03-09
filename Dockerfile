FROM python:3.11.2-slim-bullseye

MAINTAINER Carlo Eugster <carlo@relaun.ch>

RUN  apt-get update \
  && apt-get install -y wget xz-utils \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /code \
  && mkdir /jobs
WORKDIR /code
ADD . /code/
RUN pip install /code

ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV MJDL_OUT_PATH "/jobs"
ENTRYPOINT ["python", "src"]
CMD ["--help"]
