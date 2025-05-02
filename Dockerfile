FROM python:3.10

RUN mkdir /frameshelf

WORKDIR /frameshelf

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
