from collections import defaultdict
import pickle
import random

from utils import pipeName, Pipes

class Node:

    def __init__(self, node_id, balance):
        self.node_ids = []

        # Internal state
        self.id = node_id
        self.balance = balance

        # Snapshot state
        self.nodeState = 0
        self.channelState = defaultdict(int)

        # Snapshot progress
        self.receivedToken = False
        self.stopRecording = defaultdict(bool)

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
            elif command == "ReceiveAll":
                received = self.receiveAll()
                self.pipes.sendMessage(self.id, 'master', f'ack {received}')
                continue
            elif command == "CreateNode":
                self.node_ids.append(message[1])
                self.pipes.createPipe(self.id, message[1], write=True, blocking=False)
                self.pipes.createPipe(message[1], self.id, write=False, blocking=False)

            self.pipes.sendMessage(self.id, 'master', 'ack')


    def startSnapshot(self, sender):
        self.receivedToken = True

        # collect balance state
        self.nodeState = self.balance

        # record empty on channel
        if sender != 'observer':
            self.channelState[sender] = 0
            self.stopRecording[sender] = True

        # send snapshot to neighbors
        for node_id in self.node_ids:
            self.pipes.sendMessage(self.id, node_id, 'snapshot')
    
    def collect(self):
        # send state to obs
        self.pipes.sendMessage(self.id, 'observer', (self.nodeState, self.channelState))

        # reset snapshot state and progress
        self.nodeState = 0
        self.channelState = defaultdict(int)
        self.receivedToken = False
        self.stopRecording = defaultdict(bool)

    def send(self, receiver, val):
        # error check
        if val > self.balance:
            print("ERR_SEND")
            return
        else:
            # send the money
            # append sent val to channel
            self.pipes.sendMessage(self.id, receiver, str(val))
            self.balance = self.balance - val

    def receiveAll(self):
        received = False
        while self.receive(has_output=False):
            received = True
        return received

    def receive(self, sender=-1, has_output=True):
        output = None
        if sender == 'observer':
            has_output = False

        # random sender
        if sender == -1:
            message = None
            ids = random.sample(self.node_ids, len(self.node_ids))
            while message is None:
                if len(ids) == 0:
                    return False
                sender = ids.pop()
                message = self.pipes.receiveMessage(sender, self.id)
        else:
            message = self.pipes.receiveMessage(sender, self.id)

        # rid of newline
        message = message.strip()

        # start computation
        if message == "snapshot":
            output = f'{sender} SnapshotToken -1'
            if self.receivedToken:
                self.stopRecording[sender] = True
            else:
                self.startSnapshot(sender)
        elif message == 'collect':
            self.collect()
        else:
            output = f'{sender} Transfer {message}'
            self.balance = self.balance + int(message)

            # collect channel states
            if self.receivedToken and not self.stopRecording[sender]:
                self.channelState[sender] += int(message)

        if output and has_output:
            print(output)

        return True
