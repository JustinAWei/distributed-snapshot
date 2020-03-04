from collections import defaultdict
import pickle
from random import choice

class Node:
    id = -1
    balance = 0
    nodeState = 0
    channelState = defaultdict(lambda: 0)
    receivedToken = False
    stopRecording = defaultdict(lambda: False)
    allNodes = {}
    
    def listen():
        while(True):
            message = receiveMessage('master', self.id)
            
            # rid of newline
            message = message[:-1]
            message = message.split(' ')
            command = message[0]
            if command == "Send":
                _, receiver, val = message[1:]
                self.send(receiver, int(val))
            elif command == "Receive":
                # only receiver is specified
                if len(message[1:]) == 1:
                    self.receive()
                else:
                    _, sender = message[1:]
                    self.receive(sender)

    def startSnapshot(self, sender):
        self.receivedToken = True

        # collect balance state
        self.nodeState = self.balance

        # record empty on channel
        self.channelState[sender] = 0
        self.stopRecording[sender] = True

        # ack obs
        sendMessage(self.id, 'observer', 'ack')

        # send snapshot to neighbors
        for node_id in self.allNodes.keys():
            sendMessage(self.id, node_id, 'snapshot')
        return
    
    def collect(self):
        # send state to obs
        sendMessage(self.id, 'observer', pickle.dump((self.nodeState, self.channelState)))
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
            sendMessage(self.id, receiver, str(val))
            self.balance = self.balance - val

        # send a ack to master
        sendMessage(self.id, 'master', 'ack')

    def receive(self, sender=-1):
        print("recieve: r={0} s={1}\n".format(self.id, sender))

        # random sender
        if sender == -1:
            sender = random.choice(allNodes.keys())
            # while sender == self.id:
            #     sender = random.choice(allNodes.keys())

        message = receiveMessage(sender, self.id)

        print(message)

        # ack master
        sendMessage(self.id, 'master', 'ack')

        # rid of newline
        message = message[:-1]

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