from flask import Flask, request, abort, jsonify
import requests


app = Flask(__name__)

GOOGLE_GEOMAPPING_API_KEY = "AIzaSyCPqikUSY1dJtJ8jpnoUjzyGTCmVvz3DVQ"
GOOGLE_GEOMAPPING_URL = "https://maps.googleapis.com/maps/api/geocode/"
OUTPUT_FORMAT = "json"

SERVICE_URL = '/weather/api/'
SERVICE_API_VERSION = '1.0'

# "ZERO_RESULTS" indicates that the geocode was successful but returned no results.
# This may occur if the geocoder was passed a non-existent address.
# "OVER_QUERY_LIMIT" indicates that you are over your quota.
# "REQUEST_DENIED" indicates that your request was denied.
# "INVALID_REQUEST" generally indicates that the query (address, components or latlng) is missing.
# "UNKNOWN_ERROR" indicates that the request could not be processed due to a server error.
# The request may succeed if you try again.


def handle_non_existent_address(rsp):
    abort(404, detail=rsp.get('error_message', ''))


def handle_quota_reached(rsp):
    abort(503, detail=rsp.get('error_message', ''))


def handle_request_denied(rsp):
    abort(403, detail=rsp.get('error_message', ''))


def handle_invalid_address(rsp):
    abort(400, detail=rsp.get('error_message', ''))


def handle_unknown_error(rsp):
    abort(500, detail=rsp.get('error_message', ''))


GEO_STATUS_HANDLERS = {
    "ZERO_RESULTS": handle_non_existent_address,
    "OVER_QUERY_LIMIT": handle_quota_reached,
    "REQUEST_DENIED": handle_request_denied,
    "INVALID_REQUEST": handle_invalid_address,
    "UNKNOWN_ERROR": handle_unknown_error
}


@app.route(SERVICE_URL + SERVICE_API_VERSION + '/addresses/convert', methods=['GET'])
def get_coordinates():
    address = request.args.get('address')
    params = {
        'address': address,
        'key': GOOGLE_GEOMAPPING_API_KEY
    }
    rsp = requests.get(GOOGLE_GEOMAPPING_URL + OUTPUT_FORMAT, params=params)
    try:
        json_rsp = rsp.json()
        status = json_rsp['status']
        address_info = json_rsp['results'][0]
        if status == 'OK':
            coordinates = dict()
            coordinates['location'] = address_info['geometry']['location']
            return jsonify(coordinates)
        else:
            GEO_STATUS_HANDLERS.get(status, handle_unknown_error)(rsp)
    except ValueError as e:
        app.logger.error("invalid json content: %s".format(str(e)))
        raise e


if __name__ == '__main__':
    app.run()
