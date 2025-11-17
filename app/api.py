"""
This is a REST API that fetches inforamtion about staion names and shows number of available bikes and locks.
Data is fetched from Oslo Bysykkel open API.
"""

import os
import logging
import requests
import json
import datetime
from flask import Blueprint, current_app as app
from flasgger import swag_from

STATION_INFORMATION_URL = "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json"
STATION_STATUS_URL = "https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json"

"""Using the Blueprint feature of Flask to extract code to __init__.py"""
api_bp = Blueprint('api', __name__)

"""Getting logger from initialize file"""
logger = logging.getLogger(__name__)


def client_identifier_header():
    """
    Needed to stay compliant with Oslo Bysykkel API terms of use.
    I have hardcoded a default value, but it can be overridden by setting the CLIENT_IDENTIFIER environment variable in docker compose.
    """
    name = "private_use-city_bike_app"
    identifier = os.getenv("CLIENT_IDENTIFIER", name)
    return {"Client-Identifier": identifier}


def get_data(url):
    """
    Helper function to get data from a given URL.
    """
    try:
        headers = client_identifier_header()
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully processed request to {url}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.warning(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.warning(f"Other error occurred: {err}")


def get_stations():
    """
    Fetches station names and their IDs from the Oslo Bysykkel API.
    The response shape is:
    {
        "station_id": "station_name",
    }
    """
    response = get_data(STATION_INFORMATION_URL)
    if response is not None and len(response) > 1:
        stations = response["data"]["stations"]
        station_names_ids = {}
        for station in stations:
            station_names_ids[station["station_id"]] = station["name"]

        return station_names_ids
    else:
        return {}


def get_status():
    """
    Fetches number of available bikes and locks for each station from the Oslo Bysykkel API.
    The response shape is:
    {
        "station_id": {
            "num_bikes_available": int,
            "num_docks_available": int
        },
    """
    response = get_data(STATION_STATUS_URL)
    if response is not None and len(response) > 1:
        stations = response["data"]["stations"]
        station_bikes_locks = {}
        for station in stations:
            station_bikes_locks[station["station_id"]] = {
                "num_bikes_available": station["num_bikes_available"],
                "num_docks_available": station["num_docks_available"]}

        return station_bikes_locks
    else:
        return {}


@api_bp.route("/bike_status", methods=["GET"])
@swag_from({"tags": ["bike_status"]})
def bike_status():
    """
    API endpoint to get bike status. With added information about number of total stations and timestamp.
    The response shape is:
    {
        "stations": [
            {
                "station_id": int,
                "name": "sname",
                "bikes": int,
                "locks": int
            },
            …
        ],
        "total_stations": 42,
        "timestamp": "2023-10-05T12:34:56Z",
    }
    """
    station_names_ids = get_stations()
    station_status = get_status()
    stations = []
    for station_id, name in station_names_ids.items():
        bike_info = station_status.get(station_id)
        stations.append({
            "station_id": station_id,
            "name": name,
            "num_bikes_available": bike_info["num_bikes_available"],
            "num_docks_available": bike_info["num_docks_available"]
        })

    payload = {
        "stations": stations,
        "total_stations": len(stations),
        "timestamp": datetime.datetime.now().isoformat()
    }

    """Needed to do it likes this to get proper utf-8 encoding for norwegian characters"""
    response_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return app.response_class(response_json, mimetype='application/json')
