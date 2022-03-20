import zmq
import msgpack

class Ventilator():
    def __init__(self):
        context = zmq.Context()
        self.worker = context.socket(zmq.PUSH)
        self.worker.bind("tcp://*:31324")
    def send(self, tid, words):
        self.worker.send(msgpack.packb((tid, words), use_bin_type=True))