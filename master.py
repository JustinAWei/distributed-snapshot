import fileinput

def main():
    for line in fileinput.input():
        args = line.split()
        cmd = args[0]

        if cmd == 'StartMaster':
            pass
        elif cmd == 'KillAll':
            pass
        elif cmd == 'CreateNode':
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
