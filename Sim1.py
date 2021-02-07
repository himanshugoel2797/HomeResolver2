#!/usr/bin/env python36
# coding: utf-8

from Devices import *
from environment import Environment
from system import System
from request import Request

def update():
    env.update()
    sys_.process()
    sys_.show_current_state()

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

#Simulate requests from a smoke alarm
smoke_det = Request()
door_act = smoke_det.action("user0", "Door", "all", "opened", [0, 0, 100])
smoke_det.set_mandatory(door_act)
window_act = smoke_det.action("user0", "Window", "all", "opened", [0, 0, 100])
smoke_det.set_mandatory(window_act)
sys_.submit_request(smoke_det)

update()
