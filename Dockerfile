FROM python:3.11

RUN mkdir FoodShareHubDev

ADD src ./FoodShareHubDev/src
COPY ./.env ./FoodShareHubDev
COPY ./requirements.txt ./FoodShareHubDev

RUN pip install -r ./FoodShareHubDev/requirements.txt

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Singapore /etc/localtime && \
    echo "Asia/Singapore" > /etc/timezone && \
    apk del tzdata
    
WORKDIR ./FoodShareHubDev/src/app

CMD [ "python", "./main.py" ]
# ENTRYPOINT ["python ./main.py"]