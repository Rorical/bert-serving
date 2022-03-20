from tkinter.tix import Tree
import zmq
import msgpack
import uuid
import threading
import numpy as np
import threading

class Client():
    def __init__(self, pushhost="tcp://localhost:9889", pullhost="tcp://localhost:9890"):
        context = zmq.Context()

        self.pull = context.socket(zmq.PULL)
        self.pull.connect(pullhost)

        self.push = context.socket(zmq.PUSH)
        self.push.connect(pushhost)
    
        self.notify_task = {
            "id": ""
        }
        self.notify = threading.Condition()

        rec = threading.Thread(target=self.receive)
        rec.start()

    def receive(self):
        while True:
            data = msgpack.unpackb(self.pull.recv(), raw=False)
            self.notify.acquire()
            self.notify_task = data
            self.notify.notify_all()
            self.notify.release()

    def handle(self, words):
        taskid = uuid.uuid1().hex
        self.push.send(msgpack.packb({
            "id": taskid,
            "data": words
        }, use_bin_type=True))
        
        self.notify.acquire()
        while True:
            if self.notify_task["id"] == taskid:
                self.notify.release()
                result = np.frombuffer(self.notify_task["data"], dtype="float32")
                return result
            self.notify.wait()

    
if __name__ == "__main__":
    cli = Client()
    print(cli.handle(["loli", "moe"]))
        
