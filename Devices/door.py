from Devices.device import Device


class Door(Device):
    door_name = None
    def __init__(self, door_name):
        states = ["opened", "closed"]
        state_changes = {
            "opened:closed": "Close doors",
            "closed:opened": "Open doors"
        }
        self.door_name = door_name
        Device.__init__(self, "Door_%s"%(door_name), states, state_changes, {}, "closed")

    def get_resource_usage(self, state_trans, variables):
        return {}

    def update(self, sys, env):
        #if self.current_state == "opened":
        #    env.doors[self.door_name].open()
        #elif self.current_state == "closed":
        #    env.doors[self.door_name].close()
        pass

    def transition_state(self, target_state_name):
        if target_state_name in self.states:
            state_change = self.current_state + ":" + target_state_name
            for k, v in self.state_changes.items():
                if k == state_change:
                    #Device.dev_print("[%s] %s granted." % (self.name, v))  # Use value.
                    pass
            self.current_state = target_state_name
