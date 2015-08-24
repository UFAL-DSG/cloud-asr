from messages_pb2 import *

def createResultsMessage(results):
    message = ResultsListMessage()

    for (id, final, alternatives) in results:
        result = message.results.add()
        result.id.upper = id >> 64
        result.id.lower = id & ((1<<64)-1)
        result.status = ResultsMessage.SUCCESS
        result.final = final

        for (confidence, transcript) in alternatives:
            alternative = result.alternatives.add()
            alternative.confidence = confidence
            alternative.transcript = transcript

    return message

def createErrorResultsMessage():
    message = ResultsListMessage()

    result = message.results.add()
    result.status = ResultsMessage.ERROR

    return message

def parseResultsMessage(string):
    message = ResultsListMessage()
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

def createRecognitionRequestMessage(type, body, has_next, id = 0, frame_rate = 0, new_lm = ""):
    types = {
        "BATCH": RecognitionRequestMessage.BATCH,
        "ONLINE": RecognitionRequestMessage.ONLINE
    }

    message = RecognitionRequestMessage()
    message.id.upper = id >> 64
    message.id.lower = id & ((1<<64)-1)
    message.type = types[type]
    message.body = body
    message.has_next = has_next
    message.frame_rate = frame_rate
    message.new_lm = new_lm

    return message

def parseRecognitionRequestMessage(string):
    message = RecognitionRequestMessage()
    message.ParseFromString(string)

    return message

def createHeartbeatMessage(address, model, status):
    statuses = {
        "STARTED": HeartbeatMessage.STARTED,
        "WAITING": HeartbeatMessage.WAITING,
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

def createWorkerStatusMessage(address, model, status, time):
    statuses = {
        "STARTED": WorkerStatusMessage.STARTED,
        "WAITING": WorkerStatusMessage.WAITING,
        "WORKING": WorkerStatusMessage.WORKING,
    }

    message = WorkerStatusMessage()
    message.address = address
    message.model = model
    message.status = statuses[status]
    message.time = time

    return message

def parseWorkerStatusMessage(string):
    message = WorkerStatusMessage()
    message.ParseFromString(string)

    return message

def createSaverMessage(id, part, chunk_id, model, body, frame_rate, alternatives):
    message = SaverMessage()
    message.id.upper = id >> 64
    message.id.lower = id & ((1<<64)-1)
    message.part = part
    message.chunk_id.upper = chunk_id >> 64
    message.chunk_id.lower = chunk_id & ((1<<64)-1)
    message.model = model
    message.body = body
    message.frame_rate = frame_rate

    for (confidence, transcript) in alternatives:
        alternative = message.alternatives.add()
        alternative.confidence = confidence
        alternative.transcript = transcript

    return message

def parseSaverMessage(string):
    message = SaverMessage()
    message.ParseFromString(string)

    return message

def createUniqueID(id):
    uniqueId = UniqueID()
    uniqueId.upper = id >> 64
    uniqueId.lower = id & ((1<<64)-1)

    return uniqueId

def uniqId2Int(id):
    return (id.upper << 64 | id.lower)

def alternatives2List(alternatives):
    return [{"confidence": alternative.confidence, "transcript": alternative.transcript} for alternative in alternatives]
