from environment import Environment as Env

class Request:
    __weights__ = []
    __actions__ = []
    __conflicting__ = []
    __alternative__ = []
    __dependent__ = []
    __mandatory__ = []

    def __init__(self):
        pass

    def action(self, user, device, room, state, weight):
        if room != "all" or device in ["Outdoor Lights"]:
            self.__weights__.append(weight)
            self.__actions__.append({
                "user": user,
                "device": device,
                "room": room,
                "target": state,
            })
            return len(self.__actions__) - 1
        else:
            #Get list of all rooms, add entries for each
            idxs = []
            rooms = Env.get_rooms()
            for n_room in rooms:
                self.__weights__.append(weight)
                self.__actions__.append({
                    "user": user,
                    "device": "%s_%s" % (device, n_room),
                    "room": n_room,
                    "target": state,
                })
                idxs.append(len(self.__actions__) - 1)
            return idxs
                
    def set_contradicting(self, idx0, idx1):
        if type(idx0) is list:
            for i in idx0:
                self.set_contradicting(i, idx1)
        if type(idx1) is list:
            for i in idx1:
                self.set_contradicting(idx0, i)
        if idx0 < len(self.__actions__) and idx1 < len(self.__actions__):
            self.__conflicting__.append([idx0, idx1])

    def set_alternatives(self, alt_list):
        net_list = []
        for a in alt_list:
            if type(a) is list:
                for a_i in a:
                    net_list.append(a_i)
            else:
                net_list.append(a)
        self.__alternative__.append(net_list)

    def set_mandatory(self, idx):
        if type(idx) is list:
            for i in idx:
                self.__mandatory__.append(i)
        else:    
            self.__mandatory__.append(idx)

    def set_dependent(self, idx0, idx1):
        if type(idx0) is list:
            for i in idx0:
                self.set_dependent(i, idx1)
        if type(idx1) is list:
            for i in idx1:
                self.set_dependent(idx0, i)
        if idx0 < len(self.__actions__) and idx1 < len(self.__actions__):
            self.__dependent__.append([idx0, idx1])

    def read(self):
        return self.__actions__, self.__weights__, self.__mandatory__, self.__conflicting__, self.__dependent__, self.__alternative__
