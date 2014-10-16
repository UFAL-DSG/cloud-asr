from messages_pb2 import *

def createResultsMessage(final, alternatives):
    message = ResultsMessage()
    message.final = final

    for (confidence, transcript) in alternatives:
        alternative = message.alternatives.add()
        alternative.confidence = confidence
        alternative.transcript = transcript

    return message

def parseResultsMessage(string):
    message = ResultsMessage()
    message.ParseFromString(string)

    return message

def createMasterResponseMessage(status, worker_address = ""):
    statuses = {
        "SUCCESS": MasterResponseMessage.SUCCESS,
        "ERROR": MasterResponseMessage.ERROR
    }

    message = MasterResponseMessage()
    message.status = statuses[status]

    if status == "SUCCESS":
        message.address = worker_address

    return message

def parseMasterResponseMessage(string):
    message = MasterResponseMessage()
    message.ParseFromString(string)

    return message

def createWorkerRequestMessage(model):
    message = WorkerRequestMessage()
    message.model = model

    return message

def parseWorkerRequestMessage(string):
    message = WorkerRequestMessage()
    message.ParseFromString(string)

    return message

def createRecognitionRequestMessage(type, body, has_next, frame_rate = 0):
    types = {
        "BATCH": RecognitionRequestMessage.BATCH,
        "ONLINE": RecognitionRequestMessage.ONLINE
    }

    message = RecognitionRequestMessage()
    message.body = body
    message.type = types[type]
    message.has_next = has_next

    if type == "ONLINE":
        message.frame_rate = frame_rate

    return message

def parseRecognitionRequestMessage(string):
    message = RecognitionRequestMessage()
    message.ParseFromString(string)

    return message

def createHeartbeatMessage(address, model, status):
    statuses = {
        "READY": HeartbeatMessage.READY,
        "WORKING": HeartbeatMessage.WORKING,
        "FINISHED": HeartbeatMessage.FINISHED,
    }

    message = HeartbeatMessage()
    message.address = address
    message.model = model
    message.status = statuses[status]

    return message

def parseHeartbeatMessage(string):
    message = HeartbeatMessage()
    message.ParseFromString(string)

    return message
