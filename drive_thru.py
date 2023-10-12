"""
Python version: 3.7.3
SimPy version: 3.0.11
"""

import simpy
import random
import numpy as np


class Drive_thru(object):
    def __init__(self, env):
        self.env = env
        self.food_server = simpy.Resource(env, 1)
        self.order = simpy.Resource(env, 1)
        self.space_between_server = simpy.Resource(env, 1)

    def place_order(self, customer, values, env):
        order_duration = random.choice(values)
        print(f'Customer#{customer+1} is ordering.....time: {env.now}')
        yield self.env.timeout(order_duration)

    def take_food(self, customer, env, values):
        take_food_duration = random.choice(values)
        print(f'Customer#{customer+1} is taking food.....time: {env.now}')
        yield self.env.timeout(take_food_duration)

    def walking_to_food_server(self, customer, env, values):
        walking_duration = random.choice(values)
        print(
            f'Customer#{customer+1} is walking to food server.....time: {env.now}')
        yield self.env.timeout(walking_duration)

    def leaving(self, customer, env):
        print(f'Customer#{customer+1} is leaving.....time: {env.now}')
        yield self.env.timeout(0)


def arrive_at_drive_thru(env, customer, drive_thru, values_2, values_3, values_4, record):
    # customer arrives at the drive_thru
    print(f'Customer#{customer+1} is arriving.....time: {env.now}')
    record[customer].append(env.now)

    with drive_thru.order.request() as request:
        yield request
        yield env.process(drive_thru.place_order(customer, values_2, env))

    with drive_thru.space_between_server.request() as request:
        yield request
        yield env.process(drive_thru.walking_to_food_server(customer, env, values_4))

    if random.choice([True, False]):
        with drive_thru.food_server.request() as request:
            yield request
            yield env.process(drive_thru.take_food(customer, env, values_3))

    yield env.process(drive_thru.leaving(customer, env))
    record[customer].append(env.now)


def drive_thru(env, values, values_2, values_3, values_4, record):
    drive_thru = Drive_thru(env)
    customer = 0

    while True:
        record.append([])
        env.process(arrive_at_drive_thru(env, customer, drive_thru,
                    values_2, values_3, values_4, record))
        # Wait a bit before generating a new person
        yield env.timeout(random.choice(values))
        customer += 1


def main():
    # Setup
    # random.seed(42)
    size = 30
    data_record = []
    mean_selang_kedatangan = 3.0391
    standard_deviation_selang_kedatangan = 1.6927
    mean_server_1 = 1.8994
    standard_deviation_server_1 = 0.9927
    mean_server_2 = 2.1022
    standard_deviation_server_2 = 1.7617
    mean_walking = 0.47
    standard_deviation_walking = 0.65

    server_1 = list(filter(lambda x: x >= 0, [
                    random.expovariate(1/mean_server_1) for _ in range(size)]))
    arrival = list(filter(lambda x: x >= 0, [random.expovariate(
        1/mean_selang_kedatangan) for _ in range(size)]))
    server_2 = list(filter(lambda x: x >= 0, [
                    random.expovariate(1/mean_server_2) for _ in range(size)]))
    walking = list(filter(lambda x: x >= 0, [
        random.expovariate(1/mean_walking) for _ in range(size)]))

    # Run the simulation
    env = simpy.Environment()

    # print(arrival)

    print("Running simulation...")

    env.process(drive_thru(env, arrival, server_1,
                server_2, walking, data_record))
    env.run(until=90)

    print(data_record)

    data_record_filter = list(filter(lambda x: len(x) == 2, data_record))

    sum = 0
    for drive_thru_customer in data_record_filter:
        sum += drive_thru_customer[1]-drive_thru_customer[0]

    average = sum/len(data_record_filter)
    print(f'Waiting time average: {average} minute(s)')


if __name__ == "__main__":
    main()
