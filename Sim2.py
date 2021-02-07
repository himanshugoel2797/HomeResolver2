#!/usr/bin/env python36
# coding: utf-8

from Devices import *
from environment import Environment
from system import System
from request import Request

env = Environment()
sys_ = System(env)

# # # # # DEVICES # # # # #
for door_name in env.door_names:
    door = Door(door_name)
    sys_.register_device(door)

for room_name in env.room_names:
    lightsIndoor = IndoorLight(room_name)
    sys_.register_device(lightsIndoor)

    hvac = HVAC(room_name)
    sys_.register_device(hvac)

    if env.rooms[room_name].has_window():
        windows = Window(room_name)
        sys_.register_device(windows)

        blinds = Blind(room_name)
        sys_.register_device(blinds)

lightsOutdoor = OutdoorLight("Outdoor Lights")
sys_.register_device(lightsOutdoor)

batteryBackup = BatteryBackup()
sys_.register_device(batteryBackup)

# # # # # SIMULATION # # # # #
sys_.show_current_state()

#Simulate requests from outdoor lights
olights_det = Request()
olights_alts = []
for i in range(5):
    olights_on_act = olights_det.action(
        "user0", "Outdoor Lights", "all", "on_%d" % (i), [sys_.devices["Outdoor Lights"].get_resource_usage("on", {"level": i})["power"], 0, 4 + i])
    olights_mot_act = olights_det.action(
        "user0", "Outdoor Lights", "all", "motionsensor_%d" % (i), [sys_.devices["Outdoor Lights"].get_resource_usage("motionsensor", {"level": i})["power"], 0, 1 + i])

    olights_alts.append(olights_on_act)
    olights_alts.append(olights_mot_act)

olights_det.set_alternatives(olights_alts)
sys_.submit_request(olights_det)

env.update()
sys_.process()
sys_.show_current_state()
