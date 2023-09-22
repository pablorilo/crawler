from google.cloud import compute_v1
import googleapiclient.discovery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../keys/legalia-mvp-dev-386605-81840f811ef0.json"
project="legalia-mvp-dev-386605"
zone = "us-central1-a"
INSTANCE_NAME = "test-crawler"
MACHINE_TYPE = "projects/legalia-mvp-dev-386605/zones/us-central1-a/machineTypes/e2-medium"
SUBNETWORK = "regions/us-central1/subnetworks/default"
SOURCE_IMAGE = "us-central1-docker.pkg.dev/legalia-mvp-dev-386605/crawler-scripts/boe_crawler:1.0" 
NETWORK_INTERFACE = {
      "subnetwork":SUBNETWORK,
      "access_configs": [
            {
                "name": "External NAT"
            }
      ]
    }
compute_cliet = compute_v1.InstancesClient()
config = {
    "name": INSTANCE_NAME,
    "machine_type": MACHINE_TYPE,
    "disks": [
        {
        "boot": True,
        "auto_delete": True,
        "initialize_params": {
        "source_image": "projects/debian-cloud/global/images/debian-11-bullseye-v20230912"
         
        }
    }    

    ],
    "network_interfaces": [NETWORK_INTERFACE]
}

operation = compute_cliet.insert(
    project= project,
    zone = zone,
    instance_resource= config
)

operation.result()

print(f"Created VM ;{INSTANCE_NAME}")