import fileinput
from multiprocessing import Process
import os
import shutil
import sys

def pipeName(s, r):
    return './pipes/node{0}-node{1}'.format(s, r)

def sendMessage(sender, receiver, message):
    with open(pipeName(sender, receiver), 'a') as pipe:
        pipe.writeline(message)

def receiveMessage(sender, receiver):
    with open(pipeName(receiver, sender), 'r') as pipe:
        return pipe.readline(message)

class Node:
    id = -1
    balance = 0

    def send(self, receiver, val):
        print("send: sender={0} receiver={1} val={2}\n".format(id, receiver, val))
        # error check
        if val > balance:
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
        print("recieve: r={0} s={1}\n".format(id, sender))

        # TODO: random sender
        # if sender == -1:
        #     sender = random.randint(1,101)

        message = receiveMessage(sender, self.id)

        # print message
        print(message)

        # ack master
        sendMessage(self.id, 'master', 'ack')

        # rid of newline
        message = message[:-1]

        # start computation
        if message == "snapshot":
            # TODO: snapshot
            pass
        else:
            self.balance = self.balance + int(message)

def _dummyChild_(money):
    print(money)
    while True:
        pass

def _dummyObserver_():
    print("hi i'm observer")
    while True:
        pass

class Master:
    def __init__(self):
        self.nodes = dict()
        self.observer = None

    def startMaster(self):
        # Setup pipes
        shutil.rmtree('./pipes', ignore_errors=True)
        os.mkdir('./pipes')

        # Create pipe between master and observer
        os.mkfifo('./pipes/master-observer')
        os.mkfifo('./pipes/observer-master')

        # Start observer
        self.observer = Process(target=_dummyObserver_)
        self.observer.start()

    def killAll(self):
        self.observer.terminate()
        for node in self.nodes.values():
            node.terminate()
        shutil.rmtree('./pipes', ignore_errors=True)
        sys.exit()

    def createNode(self, id, money):
        # Create pipe between master and node
        os.mkfifo('./pipes/master-node{0}'.format(id))
        os.mkfifo('./pipes/node{0}-master'.format(id))

        # Create pipe from observer to node
        os.mkfifo('./pipes/observer-node{0}'.format(id))

        # Create inter-node pipes
        for node_id in range(id):
            os.mkfifo('./pipes/node{0}-node{1}'.format(id, node_id))
            os.mkfifo('./pipes/node{0}-node{1}'.format(node_id, id))

        # Start process
        p = Process(target=_dummyChild_, args=(money,))
        p.start()
        self.nodes[id] = p

    def send(self, sender, receiver, val):
        print("send: sender={0} receiver={1} val={2}\n".format(sender, receiver, val))

    def receive(self, receiver, sender):
        print("recieve: r={0} s={1}\n".format(receiver, sender))

    def receiveAll(self):
        print("recceiveAll\n")

    def beginSnapshot(self, id):
        print("beginSnapshot: id={0}\n".format(id))

    def collectState(self):
        print("collectState\n")

    def printSnapshot(self):
        print("printSnapshot\n")

# startMaster()
# killAll()
# createNode(1, 100)
# send(1,2,100)
# receive(1, 2)
# receiveAll()
# beginSnapshot(4)
# collectState()
# printSnapshot()

def run(master):
    for line in fileinput.input():
        args = line.split()
        cmd = args[0]

        if cmd == 'StartMaster':
            master.startMaster()
        elif cmd == 'KillAll':
            master.killAll()
        elif cmd == 'CreateNode':
            master.createNode(int(args[1]), int(args[2]))
        elif cmd == 'Send':
            pass
        elif cmd == 'Receive':
            pass
        elif cmd == 'ReceiveAll':
            pass
        elif cmd == 'BeginSnapshot':
            pass
        elif cmd == 'CollectState':
            pass
        elif cmd == 'PrintSnapshot':
            pass
        else:
            raise ValueError('Command not supported: ' + line)


if __name__ == '__main__':
    master = Master()
    run(master)
