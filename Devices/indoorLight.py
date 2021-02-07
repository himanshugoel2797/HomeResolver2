from Devices.device import Device


class IndoorLight(Device):
    room_name = None
    def __init__(self, name):
        states = ["on", "off"]
        state_changes = {
            "off:on": "Lights on requested",
            "on:off": "Lights off requested",
        }
        self.room_name = name
        Device.__init__(self, "Lights_%s" % (name), states, state_changes, {}, "off")

    def get_resource_usage(self, state_trans, variables):
        if state_trans.endswith("on"):
            return {
                "brightness": 1,
                "power": 8.5,
            }
        elif state_trans.endswith("off"):
            return {
                "brightness": 0,
                "power": 0,
            }
        else:
            return None

    def update(self, sys, env):
        cur_vars = self.get_resource_usage(self.current_state, self.variables)
        env.update_power(cur_vars["power"])  # Consume power
        #env.rooms[self.room_name].add_light(cur_vars["brightness"])  # Update light amount
