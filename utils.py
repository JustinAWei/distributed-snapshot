import os

def pipeName(s, r):
    return './pipes/{0}-{1}'.format(s, r)

def sendMessage(sender, receiver, msg, nonblocking=False):
    """Write message to pipe (nonblocking)."""
    # TODO - do we need newline within msg?
    msg = msg.encode()
    flags = os.O_WRONLY | (nonblocking * os.O_NONBLOCK)

    pipe = os.open(pipeName(sender, receiver), flags)
    os.write(pipe, msg)
    os.close(pipe)

def receiveMessage(sender, receiver):
    """Block until message is read from pipe."""
    with open(pipeName(sender, receiver), 'r') as pipe:
        return pipe.readline()
