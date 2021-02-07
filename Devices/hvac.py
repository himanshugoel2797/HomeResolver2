from Devices.device import Device


class HVAC(Device):
    room_name = None
    # Degrees change per second
    temperature_curve = [0, 1 / (2 * 60), 1.3 /
                         (2 * 60), 1.5 / (2 * 60), 2 / (2 * 60)]
    energy_curve = [0, 50, 125, 200, 300]

    def __init__(self, name):
        states = ["heating", "cooling", "off"]
        state_changes = {
            "off:heating": "Heating requested",
            "cooling:heating": "Heating requested",
            "off:cooling": "Cooling requested",
            "heating:cooling": "Cooling requested",
            "heating:off": "Off requested",
            "cooling:off": "Off requested"
        }
        variables = {
            "rate": 1,
        }
        Device.__init__(self, "HVAC_%s"%(name), states, state_changes, variables, "off")
        self.room_name = name

    def get_resource_usage(self, state_trans, variables):
        if state_trans.endswith("heating"):
            return {
                "power": self.energy_curve[variables["rate"]] * 1.2,
                "temperature_delta": self.temperature_curve[variables["rate"]],
            }
        elif state_trans.endswith("cooling"):
            return {
                "power": self.energy_curve[variables["rate"]],
                "temperature_delta": -self.temperature_curve[variables["rate"]],
            }
        else:
            return {
                "power": 0,
                "temperature_delta": 0,
            }

    def update(self, sys, env):
        cur_vars = self.get_resource_usage(self.current_state, self.variables)
        env.update_power(cur_vars["power"])  # Consume power
        # Update current temperature
        #env.rooms[self.room_name].update_temperature(cur_vars["temperature_delta"])

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
            self.variables["rate"] = lv
