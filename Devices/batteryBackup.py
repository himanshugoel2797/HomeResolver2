from Devices.device import Device


class BatteryBackup(Device):
    def __init__(self):
        states = ["charging", "supplying", "idle"]
        state_changes = {
            "idle:charging": "Charging",
            "supplying:charging": "Charging",
            "idle:supplying": "Supplying",
            "charging:supplying": "Supplying",
            "charging:idle": "Idle",
            "supplying:idle": "Idle"
        }
        variables = {
            "stored": 0,
            "consumption": 0,
        }
        Device.__init__(self, "Battery Backup", states, state_changes, variables, "idle")

    def get_resource_usage(self, state_trans, variables):
        return {
            "capacity": 20000 * 60 * 60,  # 20kWh
            "charging_rate": 1000,  # 1kW
        }

    def update(self, sys, env):
        cur_vars = self.get_resource_usage(self.current_state, self.variables)

        if self.current_state == "charging":
            init_stored = self.variables["stored"]
            self.variables["stored"] += cur_vars["charging_rate"]
            if self.variables["stored"] >= cur_vars["capacity"]:  # Stop charging further
                self.variables["stored"] = cur_vars["capacity"]
                self.current_state = "idle"
            env.update_power(self.variables["stored"] - init_stored)  # Consume power
        elif self.current_state == "supplying":  # Supply as much power as available
            if self.variables["stored"] >= self.variables["consumption"]:
                self.variables["stored"] -= self.variables["consumption"]
                env.update_power(-self.variables["consumption"])
            else:
                env.update_power(-self.variables["stored"])
                self.variables["stored"] = 0
                self.current_state = "idle"
