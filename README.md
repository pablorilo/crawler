==========
Legalia OS
==========


## BOE_CRAWLER

- [Description](#description)
- [Deployment](#deployment)


## Description

The BOE Crawler is a Python-based web scraping tool designed to extract information from the Boletín Oficial del Estado (BOE). This crawler automates the process of fetching and parsing data from the BOE's website, making it easier to access and analyze the content.

## Deployment

1. Make sure that you are authenticated
2. Determine the name of the image.

    ```us-central1-docker.pkg.dev/legalia-mvp-dev-386605/crawler-scripts/boe_crawler
    ```
3. Tag the local image with the repository name.

    ```docker tag {id_image} us-central1-docker.pkg.dev/legalia-mvp-dev-386605/crawler-scripts/boe_crawler:{version}
    ```

4. Push the tagged image with the command:

    ```docker push us-central1-docker.pkg.dev/legalia-mvp-dev-386605/crawler-scripts/boe_crawler:1.0
    ```








