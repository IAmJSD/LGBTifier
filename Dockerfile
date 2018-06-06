FROM python:3.6-stretch
COPY . .
RUN apt update
RUN apt install libsm6 libxext6 libxrender-dev
RUN pip install sanic imageio numpy opencv-python
EXPOSE 80
CMD python app.py
