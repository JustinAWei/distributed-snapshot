from utils import pipeName, sendMessage, receiveMessage

class Observer:
    state = {}

    def beginSnapshot(self, node_id):
        sendMessage('observer', node_id, 'snapshot')
        response = receiveMessage(node_id, 'observer')
        if (response != 'Ack'):
            raise RuntimeError('Expected \'Ack\', received {}'.format(response))
    
    def collectState(self):
        # TODO: get all nodes?
        all_node = range(5)
        for node_id in all_nodes:
            sendMessage('observer', node_id, 'collect')
            state[node_id] = receiveMessage(node_id, 'observer')

    def printSnapshot(self):
        print(state)