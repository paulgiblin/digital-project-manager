import logging
import threading
import time
from datetime import datetime, timedelta

from dpmapp import db
from dpmapp.models import SparkInfo
from dpmapp.snmpops import clients_this_interval, initialize_snmp_listener
from dpmapp.sparkops import send_spark_message, delete_spark_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(module)s:%(asctime)s: %(message)s')

file_handler = logging.FileHandler('migrateops.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

message_interval_minutes = 1
current_migration_rate = 0

threads = []


def start_migration():
    # Load existing migration window objects, then update the window to be 1 hour from now
    # Bonus goal: Extend the UI to allow user defined windows
    start_time = SparkInfo.query.filter_by(key='start_time').first()
    end_time = SparkInfo.query.filter_by(key='end_time').first()
    start_time.value = datetime.now().strftime('%H:%M')
    end_time.value = datetime.strftime((datetime.strptime(start_time.value, '%H:%M') + timedelta(hours=6)), '%H:%M')

    # Reset client counters
    # We're starting a new migration, our counters should be reset to zero
    # Bonus goal: extend the application to support migration resume after application stall/shutdown
    total_moved_clients = SparkInfo.query.filter_by(key='total_moved_clients').first()
    total_moved_clients.value = 0

    # Commit new DB values to the database
    db.session.commit()

    # Start the threaded processes
    # Bonus goal: allow the user to define an SNMP community string other than 'create' or listen on a different port
    snmp = threading.Thread(name='snmp_listener', target=initialize_snmp_listener,
                            kwargs={'community': 'create', 'port': 1620}, daemon=True)
    messages = threading.Thread(name='message_loop', target=message_loop, daemon=True)
    threads.append(snmp)
    threads.append(messages)
    snmp.start()
    messages.start()


def message_loop():
    # Send an initialization message to the Spark space
    send_spark_message('Migration monitoring process initialized')

    # Loop forever
    # Bonus goal: rewrite the loop conditions to terminate updates when the migration is complete
    while 1 == 1:
        # Update migration rate
        update_migration_rate()
        # Create the status message to send
        message = create_status_message()
        # Send the status message
        update_status(message)
        # Wait to send the next update
        time.sleep(message_interval_minutes * 60)


def update_status(message):
    # Obtain the message id of the existing Spark message
    status_message_id = SparkInfo.query.filter_by(key='status_message_id').first()
    # Delete existing status message
    delete_spark_message(status_message_id.value)
    # Send a new status message and update the message id to be that of the new message so we can delete it later
    status_message_id.value = send_spark_message(message)
    db.session.commit()


def create_status_message():
    # This message should be formatted as below
    # Status:     25% [🔵🔵🔵🔵🔵⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪]     🏎🐰🐢[8 pp/m]
    # ✅⚠️❗️[ETC 🏁 1:30:00]     🕙[Window Start/End 22:00/03:00]🕒     ⏳10% [Elapsed 00:30]
    nl = '\n'
    message = f'Status:     percent_complete()     migration_rate_string(current_migration_rate){nl}{nl}' \
              f'{estimated_time_of_completion()}     {window_times()}     {elapsed_time()}'
    return message


# def percent_complete():
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE


def update_migration_rate():
    # Count how many clients have be moved this interval
    interval_moved_client_count = len(clients_this_interval)

    # Reset the counter for the next interval
    for client in clients_this_interval:
        clients_this_interval.remove(client)

    # Update the global migration rate variable
    # Bonus goal: allow the user to define the sampling interval
    global current_migration_rate
    current_migration_rate = interval_moved_client_count / message_interval_minutes


# def migration_rate_string(ports_per_minute):
    # 🏎🐰🐢[8 pp/m]
    # Compare the p/m to some arbitrary nominal range, return a representative rate string
    # Bonus goal: allow the user to define the nominal speed
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE
    # YOUR CODE GOES HERE


def estimated_time_of_completion():
    # ✅⚠️❗️[ETC 🏁 1:30:00]
    # Calculate end time based on ports remaining * rate
    # Assumes rate is in ppm
    # Bonus goal: rewrite the application to allow the user to customize the rate to be per second, minute, hour

    # Load data on ports
    starting_clients = int(SparkInfo.query.filter_by(key='starting_clients').first().value)
    total_moved_clients = int(SparkInfo.query.filter_by(key='total_moved_clients').first().value)
    ports_remaining = starting_clients - total_moved_clients

    # If the migration is complete, say so
    if total_moved_clients == starting_clients:
        return f'✅[ETC 🏁 COMPLETE]'

    # Otherwise, load the migration window data
    start_time_string = SparkInfo.query.filter_by(key='start_time').first().value
    start_time = datetime.strptime(start_time_string, '%H:%M')
    end_time_string = SparkInfo.query.filter_by(key='end_time').first().value
    end_time = datetime.strptime(end_time_string, '%H:%M')

    # Compute the duration of the window
    window_duration = end_time - start_time

    # Update end_time to be DATE appropriate and not the year 1900 so the time delta isn't 118 years negative
    # Bonus goal: rewrite the application to support full date times and permit migrations across calendar days
    end_time = end_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

    # Compute the time at which we enter a warning condition
    # Bonus goal: Allow the user to define the safety margin
    safe_time = end_time - (window_duration * .05)

    # Compute the amount of time necessary to complete the migration - if we're not migrating, indicate we've stalled
    try:
        duration_needed_for_completion = timedelta(minutes=(ports_remaining / current_migration_rate))
    except ZeroDivisionError:
        expected_outcome_indicator = '❗'
        return f'{expected_outcome_indicator}[ETC 🏁 STALLED]'

    # Compute the actual estimated time of completion
    expected_completion_time = datetime.now() + duration_needed_for_completion

    # Compose and return the string based on the comparison of the ETC and the time parameters defined
    if expected_completion_time > end_time:
        expected_outcome_indicator = '❗'
    elif expected_completion_time < safe_time:
        expected_outcome_indicator = '✅'
    else:
        expected_outcome_indicator = '⚠️'

    return f'{expected_outcome_indicator}[ETC 🏁 {expected_completion_time.strftime("%H:%M")}]'


def window_times():
    # 🕙[Window Start/End 22:00/03:00]🕒

    # Return a string containing the window start and end times
    try:
        # These values are stored as HH:MM strings and do not need to be converted for this usage.
        start_time = SparkInfo.query.filter_by(key='start_time').first().value
        end_time = SparkInfo.query.filter_by(key='end_time').first().value
    except TypeError as e:
        logger.debug(e)
    return f'{emoji_for_time(start_time)}[Window Start/End {start_time}/{end_time}]{emoji_for_time(end_time)}'


def emoji_for_time(time):
    # Times will be coming in as HH:MM and must be converted to datetimes
    datetime_object = datetime.strptime(time, '%H:%M')

    # Round down to the nearest 30 minutes (not up, don't want 60 minutes)
    datetime_object = datetime_object + ((datetime_object.min - datetime_object) % timedelta(minutes=30))

    # Clocks only have 12 hours, so getting time as 12 hour value
    string_time = datetime_object.strftime('%I:%M')

    # Define the mapping from HH:MM string time to
    emoji_table = {
        '00:00': '🕛',
        '00:30': '🕧',
        '01:00': '🕐',
        '01:30': '🕜',
        '02:00': '🕑',
        '02:30': '🕝',
        '03:00': '🕒',
        '03:30': '🕞',
        '04:00': '🕓',
        '04:30': '🕟',
        '05:00': '🕔',
        '05:30': '🕠',
        '06:00': '🕕',
        '06:30': '🕡',
        '07:00': '🕖',
        '07:30': '🕢',
        '08:00': '🕗',
        '08:30': '🕣',
        '09:00': '🕘',
        '09:30': '🕤',
        '10:00': '🕙',
        '10:30': '🕥',
        '11:00': '🕚',
        '11:30': '🕦',
        '12:00': '🕛',
        '12:30': '🕧'
    }
    return emoji_table.get(string_time, '🕛')


def elapsed_time():
    # ⏳10% [Elapsed 00:30]
    # Get window times and current time
    start_time_string = SparkInfo.query.filter_by(key='start_time').first().value
    start_time = datetime.strptime(start_time_string, '%H:%M')
    end_time_string = SparkInfo.query.filter_by(key='end_time').first().value
    end_time = datetime.strptime(end_time_string, '%H:%M')
    current_time = datetime.now()

    # Compute time elapsed (returns a timedelta) and create a formatted string
    elapsed = current_time - start_time
    elapsed_hours = elapsed.seconds // 3600
    elapsed_minutes = (elapsed.seconds // 60) - (elapsed_hours * 60)

    # Compute window duration (timedelta)
    duration = end_time - start_time

    # Compute percentage of window time consumed
    percentage = round(elapsed.seconds/duration.seconds*100)

    return f'⏳{percentage}% [Elapsed {str(elapsed_hours).zfill(2)}:{str(elapsed_minutes).zfill(2)}]'

