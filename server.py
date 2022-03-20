from core import ventilator
from core import sink
from core import worker
from multiprocessing import Pool
import zmq
import msgpack
import threading

def Work():
    inst = worker.Worker()
    inst.serve()
    
class Server():
    def __init__(self, maxWorker=1):
        context = zmq.Context()
        
        self.pull = context.socket(zmq.PULL)
        self.pull.bind("tcp://*:9889")
        self.push = context.socket(zmq.PUSH)
        self.push.bind("tcp://*:9890")
        
        print("bind")

        self.vent = ventilator.Ventilator()
        self.sink = sink.Sink()
        print("init worker")

        self.workers = Pool(maxWorker)
        for time in range(maxWorker):
            self.workers.apply_async(Work)
        self.workers.close()
    
    def income(self):
        while True:
            task = msgpack.unpackb(self.pull.recv())
            self.vent.send(task["id"], task["data"])
        
    def outcome(self):
        while True:
            result = self.sink.receive()
            self.push.send(msgpack.packb({
                "id": result[0],
                "data": result[1]
            }, use_bin_type=True))
    
    def listen(self):
        print("start listen")
        income = threading.Thread(target=self.income)
        outcome = threading.Thread(target=self.outcome)
        income.start()
        outcome.start()
        income.join()

if __name__ == "__main__":
    server = Server(1)
    server.listen()
    
        
    