from collections import defaultdict
import pickle
import random

from utils import pipeName, Pipes

class Node:

    def __init__(self, node_id, balance):
        self.id = node_id
        self.balance = balance

        self.nodeState = 0
        self.channelState = defaultdict(lambda: 0)
        self.receivedToken = False
        self.stopRecording = defaultdict(lambda: False)
        self.allNodes = {}

        self.pipes = Pipes()
        self.pipes.createPipe(self.id, 'master', write=True, blocking=False)
        self.pipes.createPipe('master', self.id, write=False, blocking=True)

        self.pipes.createPipe(self.id, 'observer', write=True, blocking=False)
        self.pipes.createPipe('observer', self.id, write=False, blocking=False)
    
    def listen(self):
        while(True):
            message = self.pipes.receiveMessage('master', self.id)
            
            # rid of newline
            message = message.strip().split(' ')
            command = message[0]
            if command == "Send":
                _, receiver, val = message
                self.send(receiver, int(val))
            elif command == "Receive":
                # only receiver is specified
                if len(message) == 1:
                    self.receive()
                else:
                    sender = message[1]
                    self.receive(sender)
            elif command == "CreateNode":
                self.pipes.createPipe(self.id, message[1], write=True, blocking=False)
                self.pipes.createPipe(message[1], self.id, write=False, blocking=False)
                self.pipes.sendMessage(self.id, 'master', 'ack')


    def startSnapshot(self, sender):
        self.receivedToken = True

        # collect balance state
        self.nodeState = self.balance

        # record empty on channel
        self.channelState[sender] = 0
        self.stopRecording[sender] = True

        # ack obs
        self.pipes.sendMessage(self.id, 'observer', 'ack')

        # send snapshot to neighbors
        for node_id in self.allNodes.keys():
            self.pipes.sendMessage(self.id, node_id, 'snapshot')
        return
    
    def collect(self):
        # send state to obs
        self.pipes.sendMessage(self.id, 'observer', (self.nodeState, self.channelState))
        return

    def send(self, receiver, val):
        print("send: sender={0} receiver={1} val={2}\n".format(self.id, receiver, val))
        # error check
        if val > self.balance:
            print("ERR_SEND")
            print("not enough money. current balance: {}".format(self.balance))
            return
        else:
            # send the money
            # append sent val to channel
            self.pipes.sendMessage(self.id, receiver, str(val))
            self.balance = self.balance - val

        # send a ack to master
        self.pipes.sendMessage(self.id, 'master', 'ack')

    def receive(self, sender=-1):
        print("recieve: r={0} s={1}\n".format(self.id, sender))

        # random sender
        if sender == -1:
            sender = random.choice(allNodes.keys())
            # while sender == self.id:
            #     sender = random.choice(allNodes.keys())

        message = self.pipes.receiveMessage(sender, self.id)

        print(message)

        # ack master
        self.pipes.sendMessage(self.id, 'master', 'ack')

        # rid of newline
        message = message.strip()

        # start computation
        if message == "snapshot":
            if not receivedToken: startSnapshot(sender)
            else: self.stopRecording[sender] = True
        elif message == 'collect':
            collect()
        else:
            self.balance = self.balance + int(message)

            # collect channel states
            if receivedToken and not self.stopRecording[sender]:
                self.channelState[sender] = self.channelState[sender] + int(message)
