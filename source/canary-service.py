import http.server
from resource import HTML_PAGE
import socketserver
import io

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")

parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")

parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")

parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")

parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
clientId = args.clientId
topic = args.topic

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)


if not args.port:
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

logger.info("ClientID: ", clientId)
mqtt_client = None

mqtt_client = AWSIoTMQTTClient(clientId)
mqtt_client.configureEndpoint(host, port)
mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec

mqtt_client.connect()

def send_audit(client_address, honeypot_port):
    msg = {}
    msg['message'] = {"clientAddress": client_address, "serverPort": honeypot_port}
    msgJson = json.dumps(msg)
    mqtt_client.publish(topic, msgJson, 1)
    print('Published topic %s: %s\n' % (topic, msgJson))


WEB_SERVER_PORT = 80

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        send_audit(self.client_address, WEB_SERVER_PORT)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        page = HTML_PAGE
        self.wfile.write(page.encode('utf-8'))
        return


print(f'Server listening on port {WEB_SERVER_PORT}...')
httpd = socketserver.TCPServer(('', WEB_SERVER_PORT), Handler)
httpd.serve_forever()

