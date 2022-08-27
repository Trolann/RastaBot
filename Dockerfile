FROM python:3.9-alpine

ENV DISCORD_TOKEN = environ['DISCORD_TOKEN']
ENV DEV_INSTANCE = 0
ENV IRIE_GUILD_ID = environ['IRIE_GUILD_ID']

RUN mkdir -p /home/rastabot
RUN pip install discord
RUN pip install pynacl

COPY . /home/rastabot

CMD ["python3", "/home/rastabot/main.py"]