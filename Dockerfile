FROM python:3 
WORKDIR /srv
ADD ./requirements.txt /srv/requirements.txt
RUN pip install -r requirements.txt
ADD . /srv
CMD python /srv/dogmatikaWatch.py