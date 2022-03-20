import zmq
import msgpack
import numpy
from transformers import BertTokenizer, TFBertModel
import logging

class Transform():
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.model = TFBertModel.from_pretrained("bert-base-multilingual-cased")

    def extractSingle(self, word):
        encoded_input = self.tokenizer(word, return_tensors='tf')
        output = self.model(encoded_input)
        return output[1].numpy()

    def extract(self, words):
        return numpy.squeeze(sum([self.extractSingle(word) for word in words])/len(words))

class Worker():
    def __init__(self):
        context = zmq.Context()

        self.source = context.socket(zmq.PULL)
        self.source.connect('tcp://localhost:31324')

        self.sink = context.socket(zmq.PUSH)
        self.sink.connect('tcp://localhost:31325')
        
        logging.info("Initialize Transformer")
        self.transform = Transform()
    
    def serve(self):
        logging.info("Start Serving")
        while True:
            data = msgpack.unpackb(self.source.recv(), raw=False)
            result = self.transform.extract(data[1])
            self.sink.send(msgpack.packb((data[0], result.tobytes()), use_bin_type=True))