class Device:
    name = ""
    states = []  # List of state names
    state_changes = {}
    # Nested dictionary describing how a given state transition affects global resources
    resource_changes = {}
    variables = {}  # Dictionary of device variables and their values
    current_state = None  # Current device state name

    @staticmethod
    def dev_print(msg):
        GREEN = '\033[92m'  # ANSI color code for green
        END = '\033[0m'
        print(GREEN + msg + END)

    def __init__(self, init_name, init_states, init_state_changes, init_variables, init_current_state):
        self.name = init_name
        self.states = init_states
        self.state_changes = init_state_changes
        self.variables = init_variables
        if init_current_state in self.states:
            self.current_state = init_current_state
        elif len(self.states) > 0:
            self.current_state = self.states[0]

    def transition_state(self, target_state_name):
        if self.current_state != target_state_name and target_state_name in self.states:
            state_change = self.current_state + ":" + target_state_name
            for k, v in self.state_changes.items():
                if k == state_change:
                    #Device.dev_print("[%s] %s granted." % (self.name, v))  # Use value.
                    pass
            self.current_state = target_state_name

    # Set a variable's value
    def set_variable(self, var_name, var_val):
        self.variables[var_name] = var_val

    def get_resource_usage(self):
        return {}

    def update(self, sys, env):
        pass
