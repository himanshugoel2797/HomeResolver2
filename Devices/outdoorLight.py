from Devices.device import Device


class OutdoorLight(Device):
    def __init__(self, name):
        states = ["on", "off", "motionsensor"]
        state_changes = {
            "off:on": "Lights on requested",
            "on:off": "Lights off requested",
            "off:motionsensor": "Motion sensor lights requested",
            "on:motionsensor": "Motion sensor lights requested",
        }
        variables = {
            "level": 0
        }
        Device.__init__(self, name, states, state_changes, variables, "off")

    def get_resource_usage(self, state_trans, variables):
        if state_trans.endswith("on"):
            return {
                "brightness": variables["level"] * 0.25,
                "power": variables["level"] * 2.5,
            }
        elif state_trans.endswith("off"):
            return {
                "brightness": 0,
                "power": 0,
            }
        elif state_trans.endswith("motionsensor"):
            return {
                "brightness": variables["level"] * 0.25,
                # Assume an average power consumption in motion sensor mode
                "power": variables["level"] * 0.1,
            }
        else:
            return None

    def update(self, sys, env):
        cur_vars = self.get_resource_usage(self.current_state, self.variables)
        env.update_power(cur_vars["power"])  # Consume power
        #env.add_light(cur_vars["brightness"])  # Update light amount

    def transition_state(self, target_state_name):
        parts = target_state_name.split('_')
        if len(parts) > 1:
            lv = int(parts[1])
        else:
            lv = 0
        target_state_name = parts[0]
        if self.current_state != target_state_name and target_state_name in self.states:
            state_change = self.current_state + ":" + target_state_name
            for k, v in self.state_changes.items():
                if k == state_change:
                    # Use value.
                    #Device.dev_print("[%s] %s, lv: %d granted." % (self.name, v, lv))
                    pass
            self.current_state = target_state_name
            self.variables["level"] = lv
