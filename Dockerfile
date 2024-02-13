FROM python:3.11

RUN mkdir FoodShareHubDev

ADD src ./FoodShareHubDev/src
COPY ./.env ./FoodShareHubDev
COPY ./requirements.txt ./FoodShareHubDev

RUN pip install -r ./FoodShareHubDev/requirements.txt

RUN apt-get update && \
    apt-get install -y tzdata && \
    cp /usr/share/zoneinfo/Asia/Singapore /etc/localtime && \
    echo "Asia/Singapore" > /etc/timezone

WORKDIR ./FoodShareHubDev/src/app

CMD [ "python", "./main.py" ]
# ENTRYPOINT ["python ./main.py"]