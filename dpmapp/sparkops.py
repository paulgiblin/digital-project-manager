import json
import logging
import time

import requests

from dpmapp import db
from dpmapp.models import SparkInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(module)s:%(asctime)s: %(message)s')

file_handler = logging.FileHandler('sparkops.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Keep this list short to avoid having to wait for rate limiter
demo_email_list = ['pgiblin@presidio.com', 'presidionetworkengineer@sparkbot.io', 'presidiopm@sparkbot.io']


def initialize_spark(spark_token, team_name, space_name, user_email):
    # Initialize variables with existing data from the SQLite DB
    token = SparkInfo.query.filter_by(key='spark_token').first()
    teamid = SparkInfo.query.filter_by(key='teamid').first()
    roomid = SparkInfo.query.filter_by(key='roomid').first()

    # Overwrite token with new and add the submitted user to email list.
    token.value = spark_token
    db.session.commit()

    demo_email_list.append(user_email)

    # Log the collected data for troubleshooting purposes.
    logger.debug(f'User Spark Token: {spark_token}')
    logger.debug(f'Team name: {team_name}')
    logger.debug(f'Space name: {space_name}')
    logger.debug(f'User email address: {user_email}')

    # Create a Spark Team and a Spark Space INSIDE that team
    try:
        # Build the Team and add people
        teamid.value = create_spark_team(team_name)  # Create the team and store the team ID returned
        logger.debug(f"Team created - TeamID: {teamid.value}")
        add_people_to_spark_team(teamid.value, *demo_email_list)  # Add people to the team - 200 OK

        # Build the Space inside the Team and add people
        roomid.value = create_spark_team_space(teamid.value, space_name)  # Create the Space and store the ID returned
        logger.debug(f"Space created - RoomID: {roomid.value}")
        add_people_to_spark_space(roomid.value, *demo_email_list)  # Add people to the space - 200 OK

        db.session.commit()  # Load the staged data into the SQLite DB so you don't make new teams on start/stop
    except ConnectionError as e:
        logger.debug(e)


def create_spark_team(name):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    url = "https://api.ciscospark.com/v1/teams"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    payload = {
        'name': name
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    logger.debug(f'{response.url} {response.status_code} {response.json()}')
    if response.status_code == 429:
        while response.status_code != 200:
            logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
            time.sleep(response.headers['Retry-After'] + 5)
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            logger.debug(f'{response.url} {response.status_code} {response.json()}')

    return response.json()['id']


def add_people_to_spark_team(teamid, *args):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    url = "https://api.ciscospark.com/v1/team/memberships"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    for userEmail in args:
        payload = {
            'teamId': teamid,
            'personEmail': userEmail,
            'isModerator': "true"
        }
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        logger.debug(f'{response.url} {response.status_code} {response.json()}')
        if response.status_code == 429:
                while response.status_code != 200:
                    logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
                    time.sleep(response.headers['Retry-After'] + 5)
                    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
                    logger.debug(f'{response.url} {response.status_code} {response.json()}')
    return response


def create_spark_team_space(teamid, title):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    url = "https://api.ciscospark.com/v1/rooms"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    payload = {
        'teamId': teamid,
        'title': title
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    logger.debug(f'{response.url} {response.status_code} {response.json()}')
    if response.status_code == 429:
        while response.status_code != 200:
            logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
            time.sleep(response.headers['Retry-After'] + 5)
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            logger.debug(f'{response.url} {response.status_code} {response.json()}')
    return response.json()['id']


def add_people_to_spark_space(spaceid, *args):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    url = "https://api.ciscospark.com/v1/memberships"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    for userEmail in args:
        payload = {
            'roomId': spaceid,
            'personEmail': userEmail,
            'isModerator': "false"
        }
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        logger.debug(f'{response.url} {response.status_code} {response.json()}')
        if response.status_code == 429:
            while response.status_code != 200:
                logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
                time.sleep(response.headers['Retry-After'] + 5)
                response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
                logger.debug(f'{response.url} {response.status_code} {response.json()}')

    return response


def delete_spark_message(message_id):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    url = f"https://api.ciscospark.com/v1/messages/{message_id}"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    response = requests.request("DELETE", url, headers=headers)
    logger.debug(f'{response.url} {response.status_code}')
    if response.status_code == 429:
        while response.status_code != 200:
            logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
            time.sleep(response.headers['Retry-After'] + 5)
            response = requests.request("POST", url, headers=headers)
            logger.debug(f'{response.url} {response.status_code}')


def send_spark_message(message):
    spark_token = SparkInfo.query.filter_by(key='spark_token').first().value
    spaceid = SparkInfo.query.filter_by(key='roomid').first().value
    url = "https://api.ciscospark.com/v1/messages"
    headers = {
        'Authorization': f"Bearer {spark_token}",
        'Content-Type': "application/json"
    }
    payload = {
        'roomId': spaceid,
        'text': message,
        'markdown': message
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    logger.debug(f'{response.url} {response.status_code} {response.json()}')
    if response.status_code == 429:
        while response.status_code != 200:
            logger.debug(f'Waiting {response.headers["Retry-After"]} seconds due to rate limiting')
            time.sleep(response.headers['Retry-After'] + 5)
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            logger.debug(f'{response.url} {response.status_code} {response.json()}')
    return response.json()['id']
