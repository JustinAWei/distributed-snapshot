import fileinput
from multiprocessing import Process
import os
import shutil
import sys
import node

from utils import pipeName, Pipes

def _dummyChild_(node_id, money):
    pipes = Pipes()
    pipes.createPipe('master', node_id, write=False)
    pipes.createPipe(node_id, 'master', write=True)
    print('Created node with id {0}, money {1}'.format(node_id, money))
    while True:
        print('DUMMY RECV: ' + pipes.receiveMessage('master', node_id))
        pipes.sendMessage(node_id, 'master', 'Ack')

def _dummyObserver_():
    pipes = Pipes()
    pipes.createPipe('master', 'observer', write=False)
    pipes.createPipe('observer', 'master', write=True)
    print("hi i'm observer")
    while True:
        print('OBSERVER RECV: ' + pipes.receiveMessage('master', 'observer'))
        pipes.sendMessage('observer', 'master', 'Ack')

class Master:
    def __init__(self):
        self.nodes = dict()
        self.pipes = Pipes()
        self.observer = None

    def startMaster(self):
        # Setup pipes
        shutil.rmtree('./pipes', ignore_errors=True)
        os.mkdir('./pipes')

        # Create pipe between master and observer
        os.mkfifo(pipeName('master', 'observer'))
        os.mkfifo(pipeName('observer', 'master'))
        self.pipes.createPipe('master', 'observer', write=True, blocking=True)
        self.pipes.createPipe('observer', 'master', write=False, blocking=True)

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
        os.mkfifo(pipeName('master', node_id))
        os.mkfifo(pipeName(node_id, 'master'))
        self.pipes.createPipe('master', node_id, write=True, blocking=True)
        self.pipes.createPipe(node_id, 'master', write=False, blocking=True)

        # Create pipe from observer to node
        os.mkfifo(pipeName('observer', node_id))

        # Create inter-node pipes
        for neighbor_id in range(node_id):
            os.mkfifo(pipeName(node_id, neighbor_id))
            os.mkfifo(pipeName(neighbor_id, node_id))

        # Start process
        p = Process(target=_dummyChild_, args=(node_id, money))
        p.start()
        self.nodes[id] = p

    def send(self, send_id, recv_id, val):
        msg = 'Send {} {}'.format(recv_id, val)
        self.pipes.sendMessage('master', send_id, msg)

        response = self.pipes.receiveMessage(send_id, 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def receive(self, recv_id, send_id=''):
        msg = 'Receive {}'.format(send_id)
        self.pipes.sendMessage('master', recv_id, msg)

        response = self.pipes.receiveMessage(recv_id, 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def receiveAll(self):
        # TODO implement
        return

    def beginSnapshot(self, node_id):
        msg = 'BeginSnapshot {}'.format(node_id)
        self.pipes.sendMessage('master', 'observer', msg)

        response = self.pipes.receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

        receive(node_id, send_id='observer')

    def collectState(self):
        msg = 'CollectState'
        self.pipes.sendMessage('master', 'observer', msg)

        response = self.pipes.receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def printSnapshot(self):
        msg = 'PrintSnapshot'
        self.pipes.sendMessage('master', 'observer', msg)

        response = self.pipes.receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

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
            send_id = args[2] if len(args) > 2 else ''
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
