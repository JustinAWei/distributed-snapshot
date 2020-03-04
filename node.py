class Node:
    id = -1
    balance = 0
    state = 0

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
            elif command == "snapshot":
                snapshot()
            elif command == "collect":
                collect()
                pass

    def snapshot(self):
        # collect balance state
        state = balance

        # TODO: collect channel states

        # ack obs
        sendMessage(self.id, 'observer', 'ack')

        # TODO: send snapshot to neighbors
        return
    
    def collect(self):
        # send state to obs
        sendMessages(self.id, 'observer', str(state))
        return

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