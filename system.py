import cvxpy as cp
import numpy as np


class System:
    devices = {}
    requests = []
    resources = ['power_cost', 'comfort', 'security']
    resource_weights = [-1, 5, 10]
    time = 0
    rounded_time = 0
    target_temperature_present = 20
    target_temperature_absent = 20
    power_limited = False
    power_limit = 0

    def __init__(self, env):
        self.env = env

    # Name = string with device name
    # Obj = object representing interface to device, implements Device class
    def register_device(self, obj):
        self.devices[obj.name] = obj

    # Print current action set
    def show_current_state(self):
        print("At time %d.%d.%d :" % (
            self.rounded_time / (60 * 60), (self.rounded_time / 60) % 60, (self.rounded_time % 60)))
        print("\tDevices:")
        for n, o in self.devices.items():
            print("\t\t%s = %s" % (n, o.current_state))

    @staticmethod
    def action_is_duplicate(a0, a1):
        seen = set()
        new_l = []
        l = [a0, a1]

        for d in l:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        return len(new_l) == 1

    def set_max_power_limit(self, limit):
        if self.power_limited:
            self.power_limit = min(self.power_limit, limit)
        else:
            self.power_limited = True
            self.power_limit = limit

    def submit_request(self, req):
        self.requests.append(req)

    # Update action set
    def process(self):
        requested_actions = []
        weights = []
        man_actions = []
        con_action_pairs = []
        dep_action_pairs = []
        alt_actions = []
        for req in self.requests:
            requested_actions_, weights_, mandatory_actions_, \
                contradicting_action_pairs_, dependent_action_pairs_, alternative_actions_ = req.read()

            # Merge action sets
            base_idx = len(requested_actions)
            requested_actions += requested_actions_
            weights += weights_
            # alt_actions += alternative_actions_

            man_actions += [x + base_idx for x in mandatory_actions_]
            con_action_pairs += [{x[0] + base_idx, x[1] + base_idx}
                                 for x in contradicting_action_pairs_]
            dep_action_pairs += [{x[0] + base_idx, x[1] + base_idx}
                                 for x in dependent_action_pairs_]
            for x in alternative_actions_:
                s = []
                for y in x:
                    s.append(y + base_idx)
                alt_actions.append(set(s))

        # Find duplicate actions
        removed_actions = []
        for i0 in range(len(requested_actions)):
            a0 = requested_actions[i0]
            dups = []
            for i1 in range(i0 + 1, len(requested_actions)):
                a1 = requested_actions[i1]
                if System.action_is_duplicate(a0, a1):
                    dups.append(i1)

            weights_vec = weights[i0]
            for d in dups:
                # Update weights
                # Choose the action set with the highest weights
                for i in range(len(self.resources)):
                    weights_vec[i] = max(weights_vec[i], weights[d][i])

            # Update weight list
            weights[i0] = weights_vec
            for d in dups:
                weights[d] = weights_vec
                removed_actions.append(d)  # Mark duplicated actions as removed

            # Update conflict indices
            man_actions = [i0 if x in dups else x for x in man_actions]
            con_action_pairs = [set([i0 if y in dups else y for y in x])
                                for x in con_action_pairs]
            dep_action_pairs = [set([i0 if y in dups else y for y in x])
                                for x in dep_action_pairs]
            alt_actions = [set([i0 if y in dups else y for y in x])
                           for x in alt_actions]

        # Remove duplicated actions
        for d in removed_actions:
            requested_actions[d] = None

        # Different actions executing on the same device are exclusive conflicts
        for i0 in range(len(requested_actions)):
            a0 = requested_actions[i0]
            if a0 is not None:
                for i1 in range(i0 + 1, len(requested_actions)):
                    a1 = requested_actions[i1]
                    if a1 is not None and a0["device"] == a1["device"]:
                        con_action_pairs.append({i0, i1})

        # Remove duplicate conflicts
        man_actions = list(set(man_actions))

        # Convert into ILP problem
        mu = cp.Variable(len(requested_actions), integer=True,
                         boolean=True)  # whether or not the action is to be performed

        # Define constraints
        constraints = []
        for m in man_actions:
            constraints.append(mu[m] == 1)

        for e in dep_action_pairs:
            e_l = list(e)
            constraints.append(mu[e_l[0]] - mu[e_l[1]] == 0)

        for e in con_action_pairs:
            e_l = list(e)
            constraints.append(mu[e_l[0]] + mu[e_l[1]] <= 1)

        for e in alt_actions:
            e_l = list(e)
            c = mu[e_l[0]] + mu[e_l[1]]
            for idx in range(2, len(e_l)):
                c += mu[e_l[idx]]
            constraints.append(c <= 1)

        # Create power limit constraint
        if self.power_limited:
            c = None
            c_i = False
            act_idx = 0
            for i in range(len(requested_actions)):
                if requested_actions[i] is not None:
                    if not c_i:
                        c = mu[act_idx] * weights[act_idx][0]
                        c_i = True
                    else:
                        c += mu[act_idx] * weights[act_idx][0]
                    act_idx += 1
            constraints.append(c <= self.power_limit)

            print("Power limited to %f W" % (self.power_limit))

            self.power_limited = False
            #self.power_limit = 0

        # Define cost function
        cost = None
        cost_i = False
        for j in range(len(self.resource_weights)):
            c = None
            c_i = False
            act_idx = 0
            for i in range(len(requested_actions)):
                if requested_actions[i] is not None:
                    if not c_i:
                        c = mu[act_idx] * weights[act_idx][j]
                        c_i = True
                    else:
                        c += mu[act_idx] * weights[act_idx][j]
                    act_idx += 1
            if not cost_i:
                cost = c * self.resource_weights[j]
                cost_i = True
            else:
                cost += c * self.resource_weights[j]

        # Run ILP, try the ECOS_BB solver first, if it fails, use GLPK_MI
        problem = cp.Problem(cp.Maximize(cost), constraints)
        try:
            problem.solve(solver=cp.ECOS_BB)
        except:
            problem.solve(solver=cp.GLPK_MI)
        running_actions = np.round(mu.value)

        # Execute actions
        for act_idx in range(len(running_actions)):
            if requested_actions[act_idx] is not None:
                print('\033[94m[%s] %s requested.\033[0m' % (
                    self.devices[requested_actions[act_idx]["device"]].name, requested_actions[act_idx]["target"]))
        for act_idx in range(len(running_actions)):
            if requested_actions[act_idx] is not None:
                if running_actions[act_idx] == 1:
                    print('\033[92m[%s] %s granted.\033[0m' % (
                        self.devices[requested_actions[act_idx]["device"]].name, requested_actions[act_idx]["target"]))
                    self.devices[requested_actions[act_idx]["device"]].transition_state(
                        requested_actions[act_idx]["target"])  # submit action

        # Update all devices
        for dev in self.devices.values():
            dev.update(self, self.env)

        self.requests = [] #Clear the requests list for the next tick
        self.time += 1
        self.rounded_time = self.time % (24 * 60 * 60)
