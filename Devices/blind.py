from Devices.device import Device


class Blind(Device):
    room_name = None
    def __init__(self, name):
        states = ["raised", "lowered"]
        state_changes = {
            "raised:lowered": "Lower blinds",
            "lowered:raised": "Raise blinds",
        }
        variables = {
            "shutter_amount": 0
        }
        self.room_name = name
        Device.__init__(self, "Blinds_%s"%(name), states,
                        state_changes, variables, "lowered")

    def get_resource_usage(self, state_trans, variables):
        if state_trans.endswith("lowered"):
            return {
                "brightness_mult": (4 - variables["shutter_amount"]) * 0.25,
            }
        elif state_trans.endswith("raised"):
            return {
                "brightness_mult": 1,
            }
        else:
            return None

    def update(self, sys, env):
        #cur_vars = self.get_resource_usage(self.current_state, self.variables)
        #env.rooms[self.room_name].set_ambient_light_mult(cur_vars["brightness_mult"])
        pass

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
            self.variables["shutter_amount"] = lv
