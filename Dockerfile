FROM python:3.9-alpine

ENV DISCORD_TOKEN=environ['DISCORD_TOKEN']
ENV DEV_INSTANCE=0
ENV IRIE_GUILD_ID=environ['IRIE_GUILD_ID']
ENV DIR_PATH='/home/rastabot/'

RUN mkdir -p /home/rastabot
RUN pip install discord
RUN pip install pynacl
RUN pip install certifi
RUN pip install setuptools
RUN pip install attrs
RUN pip install aiohttp
RUN pip install async-timeout
RUN pip install ffmpeg
RUN pip install yarl
RUN pip install cffi
RUN pip install urllib3
RUN pip install pycparser
RUN pip install requests


COPY . /home/rastabot

CMD ["python3", "/home/rastabot/main.py"]