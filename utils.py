import os
import pickle

def pipeName(s, r):
    return './pipes/{0}-{1}'.format(s, r)

class Pipes:
    def __init__(self):
        self.pipes = dict()

    def createPipe(self, sender, receiver, write, blocking=True):
        flags = os.O_RDWR
        mode = 'wb' if write else 'rb'
        if not blocking:
            flags = flags | os.O_NONBLOCK

        name = pipeName(sender, receiver)
        fd = os.open(name, flags)
        self.pipes[name] = os.fdopen(fd, mode, buffering=0)

    def sendMessage(self, sender, receiver, msg):
        pipe = self.pipes[pipeName(sender, receiver)]
        pickle.dump(msg, pipe)

    def receiveMessage(self, sender, receiver):
        pipe = self.pipes[pipeName(sender, receiver)]
        return pickle.load(pipe)
