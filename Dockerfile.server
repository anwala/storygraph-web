FROM python:3-onbuild

LABEL maintainer="Alexander Nwala <anwala@cs.odu.edu>"

RUN pip install -r ./requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre \
    && rm -rf /var/lib/apt/lists/*

CMD ["./app.py"]