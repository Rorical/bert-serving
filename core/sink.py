import zmq
import msgpack

class Sink():
    def __init__(self):
        context = zmq.Context()
        self.worker = context.socket(zmq.PULL)
        self.worker.bind("tcp://*:31325")
    def receive(self):
        return msgpack.unpackb(self.worker.recv(), raw=False)