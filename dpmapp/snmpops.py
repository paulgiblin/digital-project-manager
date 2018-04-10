import logging

from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv

from dpmapp import db
from dpmapp.sparkops import send_spark_message
from dpmapp.models import SparkInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(module)s:%(asctime)s: %(message)s')

file_handler = logging.FileHandler('snmpops.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

clients_this_interval = []


def initialize_snmp_listener(community, port):

    # Bind SNMP to socket transport dispatcher
    snmpEngine = engine.SnmpEngine()

    # Transport setup
    # UDP over IPv4, first listening interface/port
    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode(('0.0.0.0', port))
    )
    logger.debug(f'listening on port: {port} - the standard port is 162')

    # SNMPv1/2c setup
    # SecurityName <-> CommunityName mapping
    config.addV1System(snmpEngine, 'my-area', community)

    # Register SNMP Application at the SNMP engine
    ntfrcv.NotificationReceiver(snmpEngine, handle_mac_notification)

    snmpEngine.transportDispatcher.jobStarted(1)  # this job would never finish

    # Run I/O dispatcher which would receive queries and send confirmations
    try:
        logger.debug(f"SNMP Engine running")
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        logger.debug(f"SNMP Engine failure ")
        raise


# Callback function for receiving and processing SNMP traps
def handle_mac_notification(snmpEngine, stateReference, contextEngineId, contextName,
                            varBinds, cbCtx):
    pass
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE


def port_detached_handler(switch_ip, client_mac, port):
    # Bonus goal: What other cool things could we do when a port is unplugged?
    return


def port_attached_handler(switch_ip, client_mac, port):
    pass
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
