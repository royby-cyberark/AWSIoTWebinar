import argparse
import datetime
import json
import logging
import requests
from shutil import copyfile
import threading
import time
from typing import Dict

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTThingJobsClient
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicType
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionTopicReplyType
from AWSIoTPythonSDK.core.jobs.thingJobManager import jobExecutionStatus


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--thingName", action="store", dest="thingName", help="Your AWS IoT ThingName to process jobs for")
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicJobsSampleClient",
                    help="Targeted client id")


args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
clientId = args.clientId
thingName = args.thingName

if not args.port: 
    port = 8883


logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


def rotate_cert(job_body: Dict, cert_path: str, private_key_path: str):
    rotate_cert_helper('cert', job_body, cert_path)
    rotate_cert_helper('privateKey', job_body, private_key_path)


def rotate_cert_helper(json_element: str, job_body: Dict, file_path: str):
    copyfile(file_path, file_path+".old")
    signed_url = job_body[json_element]['url']
    r = requests.get(signed_url, allow_redirects=True)
    open(file_path, 'wb').write(r.content)


class JobsMessageProcessor(object):
    def __init__(self, jobs_client, client_id):
        #keep track of this to correlate request/responses
        self.client_id = client_id
        self.jobs_client = jobs_client
        self.done = False
        self.jobs_started = 0
        self.jobs_succeeded = 0
        self.jobs_rejected = 0
        self._register_callbacks(self.jobs_client)
        self.cert_rotated = False

    def _register_callbacks(self, jobs_client):
        self.jobs_client.createJobSubscription(self.new_job_received, jobExecutionTopicType.JOB_NOTIFY_NEXT_TOPIC)
        self.jobs_client.createJobSubscription(self.start_next_job_successfully_in_progress, jobExecutionTopicType.JOB_START_NEXT_TOPIC, jobExecutionTopicReplyType.JOB_ACCEPTED_REPLY_TYPE)

    #call back on successful job updates
    def start_next_job_successfully_in_progress(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self.jobs_started += 1
            execution = payload['execution']
            self.execute_job(execution)
            status_details = {'HandledBy': 'ClientToken: {}'.format(self.client_id)}
            threading.Thread(target = self.jobs_client.sendJobsUpdate, kwargs = {'jobId': execution['jobId'], 'status': jobExecutionStatus.JOB_EXECUTION_SUCCEEDED, 'statusDetails': status_details, 'expectedVersion': execution['versionNumber'], 'executionNumber': execution['executionNumber']}).start()
        else:
            print('Start next saw no execution: ' + message.payload.decode('utf-8'))
            self.done = True

    def execute_job(self, execution):
        print('Executing job ID, version, number: {}, {}, {}'.format(execution['jobId'], execution['versionNumber'], execution['executionNumber']))
        print('With jobDocument: ' + json.dumps(execution['jobDocument']))
        if execution['jobDocument'].get('operation') == "rotate-cert":
            rotate_cert(job_body=execution['jobDocument'], cert_path=certificatePath, private_key_path=privateKeyPath)
            self.cert_rotated = True

    def new_job_received(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        if 'execution' in payload:
            self._attempt_start_next_job()
        else:
            print('Notify next saw no execution')
            self.done = True

    def process_jobs(self):
        self.done = False
        self._attempt_start_next_job()

    def _attempt_start_next_job(self):
        statusDetails = {'StartedBy': 'ClientToken: {} on {}'.format(self.client_id, datetime.datetime.now().isoformat())}
        threading.Thread(target=self.jobs_client.sendJobsStartNext, kwargs = {'statusDetails': statusDetails}).start()

    def is_done(self):
        return self.done


mqtt_client = None
mqtt_client = AWSIoTMQTTClient(clientId)
mqtt_client.configureEndpoint(host, port)
mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
mqtt_client.configureMQTTOperationTimeout(10)  # 5 sec

jobsClient = AWSIoTMQTTThingJobsClient(clientId, thingName, QoS=1, awsIoTMQTTClient=mqtt_client)

print('Connecting to MQTT server and setting up callbacks...')
jobsClient.connect()
jobsMsgProc = JobsMessageProcessor(jobsClient, clientId)
print('Starting to process jobs...')
jobsMsgProc.process_jobs()


# TODO - reconnect gracefully 
while True:
    time.sleep(2)
    if jobsMsgProc.cert_rotated:
        print("New cert detected!")
        jobsMsgProc.cert_rotated = False
        
        del jobsMsgProc
        jobsClient.disconnect()
        print("Disconnecting...")
        mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
        jobsClient = AWSIoTMQTTThingJobsClient(clientId, thingName, QoS=1, awsIoTMQTTClient=mqtt_client)
        jobsClient.connect()

        jobsMsgProc = JobsMessageProcessor(jobsClient, clientId)
        print('Starting to process jobs...')
        jobsMsgProc.process_jobs()
