from utils import pipeName, Pipes

class Observer:

    def __init__(self):
        self.state = {}
        self.node_ids = []

        self.pipes = Pipes()
        self.pipes.createPipe('observer', 'master', write=True, blocking=False)
        self.pipes.createPipe('master', 'observer', write=False, blocking=True)

    def listen(self):
        while(True):
            message = self.pipes.receiveMessage('master', 'observer')
            
            # rid of newline
            message = message.strip().split(' ')
            command = message[0]

            if command == 'BeginSnapshot':
                node_id = message[1]
                self.beginSnapshot(node_id)
            elif command == 'CollectState':
                self.collectState()
            elif command == 'PrintSnapshot':
                self.printSnapshot()
            elif command == "CreateNode":
                self.node_ids.append(message[1])
                self.pipes.createPipe('observer', message[1], write=True, blocking=False)
                self.pipes.createPipe(message[1], 'observer', write=False, blocking=True)
                self.pipes.sendMessage('observer', 'master', 'ack')

    def beginSnapshot(self, node_id):
        print(f'Started by Node {node_id}')
        self.pipes.sendMessage('observer', node_id, 'snapshot')
        self.pipes.sendMessage('observer', 'master', 'ack')
    
    def collectState(self):
        # TODO sort?
        for node_id in sorted(self.node_ids):
            self.pipes.sendMessage('observer', node_id, 'collect')
            self.pipes.sendMessage('observer', 'master', f'ack {node_id}')
            self.state[node_id] = self.pipes.receiveMessage(node_id, 'observer')
        self.pipes.sendMessage('observer', 'master', 'ack')

    def printSnapshot(self):
        print('---Node states')
        for node_id in sorted(self.node_ids):
            print(f'node {node_id} = {self.state[node_id][0]}')

        print('---Channel states')
        for src_id in sorted(self.node_ids):
            for dest_id in sorted(self.node_ids):
                if src_id != dest_id:
                    print(f'channel ({src_id} -> {dest_id}) = {self.state[dest_id][1][src_id]}')

        self.pipes.sendMessage('observer', 'master', 'ack')
