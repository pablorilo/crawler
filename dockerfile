# Utiliza una imagen base
FROM openjdk:8-jre

# Set environmental variables
ENV AIRFLOW_HOME=/home/user/airflow

#Copy requirements
COPY packages.txt python_requirements.txt /

RUN apt-get update && \
    apt-get install -y gosu supervisor python3 python3-pip virtualenv gettext-base gzip && \
    apt-get clean

# Install Python requirements
RUN pip3 install -r /python_requirements.txt && \
    rm /python_requirements.txt

#Google cloud commnad line
RUN wget -qO- https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-381.0.0-linux-x86_64.tar.gz | tar xvz -C /opt  \
    && cd /opt/google-cloud-sdk && ./install.sh --usage-reporting false --quiet

# Copy configuration files
COPY airflow.cfg $AIRFLOW_HOME/
COPY supervisord.conf /home/user/supervisor/conf.d/supervisord.conf
#COPY keys/keys.json  /home/user/keys/keys.json
RUN mkdir /home/user/supervisor/logs

#set GOOGLE_APPLICATION_CREDENTIALS
#ENV GOOGLE_APPLICATION_CREDENTIALS=/home/user/keys/keys.json

#copy dags file
COPY /dags/ $AIRFLOW_HOME/dags

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR $AIRFLOW_HOME

EXPOSE 8080 9001
ENTRYPOINT [ "/entrypoint.sh" ]

# CMD para iniciar el servicio web de Airflow y el planificador
CMD ["/usr/bin/supervisord","-c","/home/user/supervisor/conf.d/supervisord.conf"]