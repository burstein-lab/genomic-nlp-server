FROM python:3.10
ADD . /opt/webapp/
WORKDIR /opt/webapp

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy

# Expose is NOT supported by Heroku
# EXPOSE 5000 		

## Run the image as a non-root user
#RUN adduser --disabled-login myuser
#USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD pipenv run gunicorn --bind 0.0.0.0:$PORT wsgi 
