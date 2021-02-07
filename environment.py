import math


class DoorNode:
    in_room = None
    out_room = None

    def __init__(self, in_room, out_room):
        self.in_room = in_room
        self.out_room = out_room


class Room:
    doors = {}  # Names of rooms the doors connect to
    windows = []  # List of windows

    def __init__(self, name, env):
        self.name = name
        self.env = env

    def add_door(self, tgt_room_name, door):
        self.doors[tgt_room_name] = door

    def has_window(self):
        return len(self.windows) > 0

    def add_window(self):
        self.windows.append(False)


class Environment:
    time = 0
    power_consumed_instant = 0
    power_consumed_instant_delta = 0
    electricity_rate_base = 0.115 / (60 * 60 * 1000)
    electricity_rate = 0.115 / (60 * 60 * 1000)  # $0.115/kWh to $/Ws
    electricity_rate_delta = 0
    
    rooms = {}
    room_names = []
    doors = {}
    door_names = []

    @staticmethod
    def get_rooms():
        return ["bedroom0", "bedroom1", "kitchen", "bathroom", "livingroom"]

    def __init__(self):
        # Setup rooms, doors and windows
        bd0 = Room("bedroom0", self)
        bd0.add_window()

        bd1 = Room("bedroom1", self)
        bd1.add_window()

        ktch = Room("kitchen", self)
        ktch.add_window()

        bathroom = Room("bathroom", self)

        livingroom = Room("livingroom", self)
        livingroom.add_window()

        bd0_exit = DoorNode(bd0, livingroom)
        bd1_exit = DoorNode(bd1, livingroom)
        ktch_exit = DoorNode(ktch, livingroom)
        bathroom_exit = DoorNode(bathroom, livingroom)
        main_door = DoorNode(livingroom, None)

        bd0.add_door("livingroom", bd0_exit)
        bd1.add_door("livingroom", bd1_exit)
        ktch.add_door("livingroom", ktch_exit)
        bathroom.add_door("livingroom", bathroom_exit)

        livingroom.add_door("bedroom0", bd0_exit)
        livingroom.add_door("bedroom1", bd1_exit)
        livingroom.add_door("kitchen", ktch_exit)
        livingroom.add_door("bathroom", bathroom_exit)
        livingroom.add_door("livingroom", main_door)

        self.rooms["bedroom0"] = bd0
        self.rooms["bedroom1"] = bd1
        self.rooms["kitchen"] = ktch
        self.rooms["bathroom"] = bathroom
        self.rooms["livingroom"] = livingroom
        self.room_names = self.rooms.keys()

        self.doors["bedroom0"] = bd0_exit
        self.doors["bedroom1"] = bd1_exit
        self.doors["kitchen"] = ktch_exit
        self.doors["bathroom"] = bathroom_exit
        self.doors["livingroom"] = main_door
        self.door_names = self.doors.keys()

    def update_power(self, p):
        self.power_consumed_instant_delta += p

    def set_electricity_rate(self, r):
        self.electricity_rate_delta = r - self.electricity_rate

    def update(self):
        self.time += 1
        self.power_consumed_instant = self.power_consumed_instant_delta
        self.power_consumed_instant_delta = 0

        self.electricity_rate = self.electricity_rate_base * \
            (1 + (0.5 * math.sin(self.time * math.pi / (12 * 60 * 60)) + 0.5)
             * 0.3) + self.electricity_rate_delta
