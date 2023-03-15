import numpy as np


def exp_randomvalue(mean):
    return np.random.exponential(mean, 1)[0]


SIMTIME_LIMIT = 80 * 6
people_arrive_mean = 12
call_arrive_mean = 10
people_service_mean = 6
call_service_mean = 5
busy, free = 1, 0
calls_delay_info, people_queue_change_register, call_queue, people_queue, \
    clock, people_attended, calls_attended, server_status,\
    server_change_register, call_queue_change_register, people_delay_info = [
    None for i in range(11)]

events_list = [0, 0, 0, 0]


# event1 -> people arrive
# event2 -> call arrive
# event3 -> service
# event4 -> service ending (time reached)

def init_simulation():
    global calls_delay_info, people_queue_change_register, call_service_mean, people_service_mean, call_arrive_mean, SIMTIME_LIMIT, people_arrive_mean,\
        call_queue, people_queue, clock, people_attended, calls_attended, server_status, server_change_register, call_queue_change_register, people_delay_info, events_list
    # Performance measures variables init
    server_change_register = []
    call_queue_change_register = []
    people_queue_change_register = []
    people_delay_info = []
    calls_delay_info = []
    people_attended = []
    calls_attended = []
    # State variables init
    call_queue = []
    people_queue = []
    server_status = free
    # Counter values init
    people_wait_time = 0
    call_wait_time = 0
    people_attended = 0
    calls_attended = 0
    last_call_time = 0
    # clock init
    clock = 0.0
    # events_init --> We program first events
    events_list[0] = 2
    events_list[1] = 3
    events_list[2] = 1e10
    events_list[3] = SIMTIME_LIMIT


def general_service():
    global events_list, call_queue, people_queue, server_status
    if len(people_queue) != 0:
        people_service()
    else:
        if len(call_queue) != 0:
            call_service()
        else:
            server_status = free
            server_change_register.append((clock, server_status))
            events_list[2] = 1e10


def people_service(n_queue_costumer=1e10):
    global people_service_mean, people_attended, clock, people_delay_info,\
        events_list, people_queue, SIMTIME_LIMIT, server_status, server_change_register, people_queue_change_register
    # Increase people attended in one
    people_attended += 1
    if server_status == free:
        server_status = busy
        server_change_register.append((clock, server_status))
    # Check state of next person to attend
    if n_queue_costumer > SIMTIME_LIMIT:
        client_attended_arrive_time = people_queue.pop(0)
        people_queue_change_register.append((clock, len(people_queue)))
        delay_time = clock - client_attended_arrive_time
    else:
        delay_time = 0
    # Save delay information for performance
    people_delay_info.append(delay_time)
    # Update event type 3
    service_time = exp_randomvalue(people_service_mean)
    events_list[2] = clock + service_time
    # print(f'with mean = {people_service_mean} we get random value {service_time} where clock is {clock} and next event of type 2 is programmed at {events_list[2]}')


def call_service(n_queue_costumer=1e10):
    global call_service_mean, calls_attended, clock, calls_delay_info, events_list, call_queue, SIMTIME_LIMIT, server_status, server_change_register, call_queue_change_register
    # Increase people attended in one
    calls_attended += 1
    if server_status == free:
        server_status = busy
        server_change_register.append((clock, server_status))
    # Check state of next person to attend
    if n_queue_costumer > SIMTIME_LIMIT:
        client_attended_arrive_time = call_queue.pop(0)
        call_queue_change_register.append((clock, len(call_queue)))
        delay_time = clock - client_attended_arrive_time
    else:
        delay_time = 0
    # Save delay information for performance
    calls_delay_info.append(delay_time)
    # Update event type 3
    service_time = exp_randomvalue(call_service_mean)
    events_list[2] = clock + service_time
    # print(f'with mean = {call_service_mean} we get random value {service_time} where clock is {clock} and next event of type 2 is programmed at {events_list[2]}')


def people_arrive():
    global events_list, people_arrive_mean, people_queue, server_status, people_queue_change_register
    client = events_list[0]
    # Update event type 1
    new_event = exp_randomvalue(people_arrive_mean)
    events_list[0] = clock + new_event
    # print(f'with mean = {people_arrive_mean} we get random value {new_event} where clock is {clock} and next event of type 0 is programmed at {events_list[0]}')
    # Check conditions and define actions
    if server_status == free:
        if len(people_queue) == 0:
            people_service(client)
        else:
            people_queue.append(client)
            people_queue_change_register.append((clock, len(people_queue)))
    else:
        people_queue.append(client)
        people_queue_change_register.append((clock, len(people_queue)))


def call_arrive():
    global events_list, call_arrive_mean, call_queue, people_queue, server_status, call_queue_change_register
    client = events_list[1]
    # Program next arrive
    # Update event type 2
    new_event = exp_randomvalue(call_arrive_mean)
    events_list[1] = clock + new_event
    # print(f'with mean = {call_arrive_mean} we get random value {new_event} where clock is {clock} and next event of type 1 is programmed at {events_list[1]}')
    # Check conditions and define actions
    if len(people_queue) == 0:
        if server_status == free:
            if len(call_queue) == 0:
                call_service(client)
            else:
                call_queue.append(client)
                call_queue_change_register.append((clock, len(call_queue)))
        else:
            call_queue.append(client)
            call_queue_change_register.append((clock, len(call_queue)))
    else:
        call_queue.append(client)
        call_queue_change_register.append((clock, len(call_queue)))


def simulation_timing_process():
    global events_list, clock, server_status, people_queue, call_queue
    init_simulation()
    while min(events_list) != events_list[3]:
        # print(f'\nBefore process, event_list is {events_list} and server_status is {server_status} and clock {clock} -- people_q={len(people_queue)} -- call_q={len(call_queue)}')
        time_next_laps = min(events_list)
        clock = time_next_laps
        # print(clock,events_list)
        if min(events_list) == events_list[0]:
            people_arrive()
        elif min(events_list) == events_list[1]:
            call_arrive()
        elif min(events_list) == events_list[2]:
            general_service()
        # print(f'After process, event_list is {events_list} and server_status is {server_status} and clock {clock} -- people_q={len(people_queue)} -- call_q={len(call_queue)}\n')


def results_generation():
    global people_attended, calls_attended, people_delay_info, calls_delay_info
    print(f'Servidor: {people_attended} personas y {calls_attended} llamadas')
    people_queue_waittime_mean = sum(people_delay_info) / len(people_delay_info)
    calls_queue_waittime_mean = sum(calls_delay_info) / len(calls_delay_info)
    print(f'Espera promedio personas: {people_queue_waittime_mean} minutos')
    print(f'Espera promedio llamadas: {calls_queue_waittime_mean} minutos')


simulation_timing_process()
results_generation()
