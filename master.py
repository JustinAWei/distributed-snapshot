import fileinput
from multiprocessing import Process
import os

nodes = dict()

def _dummyChild_(money):
    print(money)
    while True:
        pass

def startMaster():
    print("startMaster\n")

def killAll():
    print("killAll\n")

def createNode(id, money):
    # Create pipe from master to node
    os.mkfifo('./pipes/master-node{0}'.format(id))

    # Create pipe from observer to node
    os.mkfifo('./pipes/observer-node{0}'.format(id))

    # Create inter-node pipes
    for node_id in range(id):
        os.mkfifo('./pipes/node{0}-node{1}'.format(id, node_id))
        os.mkfifo('./pipes/node{0}-node{1}'.format(node_id, id))

    # Start process
    p = Process(target=_dummyChild_, args=(money,))
    p.start()
    nodes[id] = p

def send(sender, receiver, val):
    print("send: sender={0} receiver={1} val={2}\n".format(sender, receiver, val))

def receive(receiver, sender):
    print("recieve: r={0} s={1}\n".format(receiver, sender))

def receiveAll():
    print("recceiveAll\n")

def beginSnapshot(id):
    print("beginSnapshot: id={0}\n".format(id))

def collectState():
    print("collectState\n")

def printSnapshot():
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

def main():
    for line in fileinput.input():
        args = line.split()
        cmd = args[0]

        if cmd == 'StartMaster':
            pass
        elif cmd == 'KillAll':
            pass
        elif cmd == 'CreateNode':
            createNode(int(args[1]), int(args[2]))
            pass
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
    main()
