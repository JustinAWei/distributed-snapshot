import os

def pipeName(s, r):
    return './pipes/{0}-{1}'.format(s, r)

def sendMessage(sender, receiver, msg):
    """Write message to pipe (nonblocking)."""
    msg = (msg + '\n').encode()

    pipe = os.open(pipeName(sender, receiver), os.O_WRONLY | os.O_NONBLOCK)
    os.write(pipe, msg)
    os.close(pipe)

def receiveMessage(sender, receiver):
    """Block until message is read from pipe."""
    with open(pipeName(receiver, sender), 'r') as pipe:
        return pipe.readline()
