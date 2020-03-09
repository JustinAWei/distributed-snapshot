from utils import pipeName, sendMessage, receiveMessage

class Observer:
    state = {}
    allNodes = {}

    def beginSnapshot(self, node_id):
        sendMessage('observer', node_id, 'snapshot')
        response = receiveMessage(node_id, 'observer')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))
    
    def collectState(self):
        for node_id in self.allNodes.keys():
            sendMessage('observer', node_id, 'collect')
            self.state[node_id] = receiveMessage(node_id, 'observer')

    def printSnapshot(self):
        print(self.state)