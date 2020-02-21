import fileinput
from multiprocessing import Process
import os
import shutil
import sys

from utils import pipeName, sendMessage, receiveMessage


class Node:
    id = -1
    balance = 0

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
            elif command == "ReceiveAll":
                pass

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


def _dummyChild_(node_id, money):
    print('Created node with id {0}, money {1}'.format(node_id, money))
    while True:
        print('DUMMY RECV: ' + receiveMessage('master', node_id))
        sendMessage(node_id, 'master', 'Ack', nonblocking=True)

def _dummyObserver_():
    print("hi i'm observer")
    while True:
        print('OBSERVER RECV: ' + receiveMessage('master', 'observer'))
        sendMessage('observer', 'master', 'Ack', nonblocking=True)

class Master:
    def __init__(self):
        self.nodes = dict()
        self.observer = None

    def startMaster(self):
        # Setup pipes
        shutil.rmtree('./pipes', ignore_errors=True)
        os.mkdir('./pipes')

        # Create pipe between master and observer
        os.mkfifo(pipeName('master', 'observer'))
        os.mkfifo(pipeName('observer', 'master'))

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
        sendMessage('master', send_id, msg)

        response = receiveMessage(send_id, 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def receive(self, recv_id, send_id=''):
        msg = 'Receive {}'.format(send_id)
        sendMessage('master', recv_id, msg)

        response = receiveMessage(recv_id, 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def receiveAll(self):
        # TODO implement
        return

    def beginSnapshot(self, node_id):
        msg = 'BeginSnapshot {}'.format(node_id)
        sendMessage('master', 'observer', msg)

        response = receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

        receive(node_id, send_id='observer')

    def collectState(self):
        msg = 'CollectState'
        sendMessage('master', 'observer', msg)

        response = receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

    def printSnapshot(self):
        msg = 'PrintSnapshot'
        sendMessage('master', 'observer', msg)

        response = receiveMessage('observer', 'master')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))

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
