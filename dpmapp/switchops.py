import logging
from dpmapp import db
from dpmapp.models import SparkInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(module)s:%(asctime)s: %(message)s')

file_handler = logging.FileHandler('switchops.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def initialize_switches(src_switch_ip, dst_switch_ip, clients):
    source_switch_ip = SparkInfo.query.filter_by(key='source_switch_ip').first()
    source_switch_ip.value = str(src_switch_ip)

    destination_switch_ip = SparkInfo.query.filter_by(key='destination_switch_ip').first()
    destination_switch_ip.value = str(dst_switch_ip)

    starting_clients = SparkInfo.query.filter_by(key='starting_clients').first()
    starting_clients.value = str(clients)

    db.session.commit()

    logger.debug(f'Updated Source Switch IP: {source_switch_ip.value}')
    logger.debug(f'Updated Destination Switch IP: {destination_switch_ip.value}')
    logger.debug(f'Updated Initial Client Count: {starting_clients.value}')
