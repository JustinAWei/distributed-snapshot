import fileinput
from multiprocessing import Process
import os
import shutil
import sys

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
