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

    def createNode(self, node_id, money):
        # Create pipe between master and node
        os.mkfifo('./pipes/master-node{0}'.format(id))
        os.mkfifo('./pipes/node{0}-master'.format(id))

        # Create pipe from observer to node
        os.mkfifo('./pipes/observer-node{0}'.format(id))

        # Create inter-node pipes
        for neighbor_id in range(node_id):
            os.mkfifo('./pipes/node{0}-node{1}'.format(node_id, neighbor_id))
            os.mkfifo('./pipes/node{0}-node{1}'.format(neighbor_id, node_id))

        # Start process
        p = Process(target=_dummyChild_, args=(money,))
        p.start()
        self.nodes[id] = p

    def send(self, send_id, recv_id, val):
        return

    def receive(self, recv_id, send_id=None):
        return

    def receiveAll(self):
        return

    def beginSnapshot(self, id):
        return

    def collectState(self):
        return

    def printSnapshot(self):
        return

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
        for idx in range(1, len(args)):
            args[idx] = int(args[idx])

        if cmd == 'StartMaster':
            master.startMaster()
        elif cmd == 'KillAll':
            master.killAll()
        elif cmd == 'CreateNode':
            node_id = args[1]
            money = args[2]
            master.createNode(node_id, money)
        elif cmd == 'Send':
            send_id = args[1]
            recv_id = args[2]
            money = args[3]
            master.send(send_id, recv_id, money)
        elif cmd == 'Receive':
            recv_id = args[1]
            send_id = args[2] if len(args) > 2 else None
            master.receive(recv_id, send_id)
        elif cmd == 'ReceiveAll':
            master.receiveAll()
        elif cmd == 'BeginSnapshot':
            node_id = args[1]
            master.beginSnapshot(node_id)
        elif cmd == 'CollectState':
            master.collectState()
        elif cmd == 'PrintSnapshot':
            master.printSnapshot()
        else:
            raise ValueError('Command not supported: ' + line)


if __name__ == '__main__':
    master = Master()
    run(master)
