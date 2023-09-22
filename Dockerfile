FROM python:3.9.13

WORKDIR /app

COPY legalia-mvp-dev-386605-81840f811ef0.json /app/credenciales.json


# Establece la variable de entorno GOOGLE_APPLICATION_CREDENTIALS
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credenciales.json
ENV PYTHONPATH /usr/local/lib/python3.8/site-packages


COPY requirements.txt requirements.txt
RUN python3 -m pip install keyring \
    && python3 -m pip install keyrings.google-artifactregistry-auth \
    && pip3 config set global.extra-index-url https://us-central1-python.pkg.dev/legalia-mvp-dev-386605/legalia-os/simple 
RUN pip3 install -r requirements.txt

COPY main.py .

CMD [ "python3", "main.py" ]
