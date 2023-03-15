import math
import random
from queue import Queue
from typing import Tuple

IDLE = 0
BUSY = 1

time_next_event = {
    "Arrival": 0.0,
    "Departure ": 0.0
}

SIMTIME_LIMIT = 480
clock = 0.0
delay_in_q = 0.0
total_utilities = None
server_status = IDLE
customers_in_q = 0.0
arrivals_queue = Queue()
attended_customers = 0


def random_customer() -> tuple[int, int]:
    u = random.uniform(0.0, 1.0)
    if u <= 0.2:
        return 1, 0
    elif 0.2 < u <= 0.7:
        return 2, 2500
    elif u > 0.7:
        return 3, 4500


def random_exponential(given_mean):
    u = random.uniform(0.0, 1.0)

    while u == 0.0:
        u = random.uniform(0.0, 1.0)

    return -given_mean * math.log(u)


def service_time_a_customer():
    u = random.uniform(0.0, 1.0)
    return 3.1 + (u * (3.4 - 3.1))


def departure_selector(type_customer):
    if type_customer == 1:
        service_time = 1.5
    elif type_customer == 2:
        service_time = service_time_a_customer()
    else:
        service_time = random_exponential(7)

    return service_time


def initialize():
    global clock, total_utilities, delay_in_q, time_next_event, server_status, customers_in_q
    clock = 0.0

    total_utilities = 0.0
    delay_in_q = 0.0
    server_status = 0
    customers_in_q = 0

    time_next_event["Arrival"] = clock + random_exponential(3)
    time_next_event["Departure"] = float('inf')


def arrival():
    global customers_in_q, time_next_event, clock, delay_in_q, server_status, BUSY, total_utilities
    time_next_event["Arrival"] = random_exponential(1.5)  # Next arrival scheduled

    if server_status == BUSY:
        customers_in_q += 1
        arrivals_queue.put(clock)
    else:
        delay = 0.0
        delay_in_q += delay

        server_status = BUSY
        customer_type, utility = random_customer()
        total_utilities += utility
        time_next_event["Departure"] = departure_selector(customer_type)


def departure():
    global customers_in_q, clock, IDLE, delay_in_q, attended_customers, server_status, total_utilities
    if customers_in_q == 0:
        server_status = IDLE
        time_next_event["Departure"] = float('inf')
    else:
        delay = clock - arrivals_queue.get()
        customers_in_q -= 1
        delay_in_q += delay
        attended_customers += 1
        customer_type, utility = random_customer()
        total_utilities += utility
        time_next_event["Departure"] = departure_selector(customer_type)


def timing():
    global clock, time_next_event
    event = min(time_next_event["Arrival"], time_next_event["Departure"])
    clock += event
    return event


def new_timing():
    global clock, time_next_event
    event = time_next_event["Departure"]
    clock += event
    return event


def main_routine():
    global SIMTIME_LIMIT, time_next_event, clock, customers_in_q, delay_in_q
    initialize()
    while clock < SIMTIME_LIMIT:
        time = timing()
        if time == time_next_event["Arrival"]:
            arrival()
        if time == time_next_event["Departure"]:
            departure()

    time_next_event["Arrival"] = float('inf')

    while customers_in_q > 0:
        new_time = new_timing()
        if new_time == time_next_event["Departure"]:
            departure()
        departure()


def report():
    global delay_in_q, attended_customers, clock, total_utilities, time_next_event
    print("Total utilities in this day: " + str(total_utilities))
    print("Attended Customers " + str(attended_customers))
    print("Average delay in queue: " + str((delay_in_q / attended_customers) / 60))
    print("Employee hour of departure: " + str(clock / 60))
    #print("Last departure: " + str(time_next_event["Departure"]))


main_routine()
report()
