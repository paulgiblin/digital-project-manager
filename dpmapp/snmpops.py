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
    # Extract transport information tuple
    (transportDomain, transportAddress) = snmpEngine.msgAndPduDsp.getTransportInfo(stateReference)
    logger.debug(f"SNMP Notifications from IP: {transportAddress[0]}")

    # Iterate through received data
    for name, val in varBinds:
        # Only parse the mac-notification data
        if name.prettyPrint() == '1.3.6.1.4.1.9.9.215.1.1.8.1.2.1':
            trapInfo = str(val.prettyPrint())
            notificationTrapMacChangeType = trapInfo[2:4]
            notificationTrapVlan = str(int(trapInfo[4:8], 16))
            notificationTrapMac = trapInfo[8:20]
            notificationTrapPort = str(int(trapInfo[20:24], 16))

            # Handle client detached event
            if notificationTrapMacChangeType == '02':
                message = f'MAC Address: {notificationTrapMac.upper()} has been detached from port: ' \
                          f'{notificationTrapPort} on Switch: {transportAddress[0]} Access VLAN: {notificationTrapVlan}'
                logger.debug(message)
                send_spark_message(message)
                port_detached_handler(transportAddress[0], notificationTrapMac, notificationTrapPort)

            # Handle client attached event
            elif notificationTrapMacChangeType == '01':
                message = f'MAC Address: {notificationTrapMac.upper()} has been attached to port: ' \
                          f'{notificationTrapPort} on Switch: {transportAddress[0]} Access VLAN: {notificationTrapVlan}'
                logger.debug(message)
                send_spark_message(message)
                port_attached_handler(transportAddress[0], notificationTrapMac, notificationTrapPort)


def port_detached_handler(switch_ip, client_mac, port):
    # Bonus goal: What other cool things could we do when a port is unplugged?
    return


def port_attached_handler(switch_ip, client_mac, port):
    # Only increment if the switch sending the attach notification is the destination device
    destination_switch_ip = SparkInfo.query.filter_by(key='destination_switch_ip').first().value
    if destination_switch_ip == switch_ip:
        total_moved_clients = SparkInfo.query.filter_by(key='total_moved_clients').first()
        total_moved_clients.value = 1 + int(total_moved_clients.value)
        db.session.commit()
        clients_this_interval.append(client_mac)  # Global variable in the migrateops module
    return
