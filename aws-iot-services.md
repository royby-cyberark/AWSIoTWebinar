# AWS IoT Services and Features

## AWS IoT Core
The core service AWS IoT has to offer which we will focus on.

### Onboarding
One or more "Thing" provisioning. This includes creatoin and registration of a device, or "thing", download of the SDK that fits your needs, and setting some thing meta data, like thing type and attributes.

### Management
* Thing types - ease mangement by giving devices the same type and set of properties 
* Static groups - group things together which allows managing multiple things at once
* Dynamic groups - group based on device state which can change, for example, can be used to update devices that are with 80% battery or more

### Client Authentication
* AWS IoT provides secure means of authenticating things to the backend whinin AWS's shared responsibility model
* We will focus on X.509 client certificates, i which you create a certificate in the IoT service, register it, assign it and provide it to the device.
  This will allow the device to communicate to the IoT Service as we will see soon.
* Another interesting way to authenticate is allowing for direct access to AWS Services.
  * https://docs.aws.amazon.com/iot/latest/developerguide/authorizing-direct-aws.html
  * https://aws.amazon.com/blogs/security/how-to-eliminate-the-need-for-hardcoded-aws-credentials-in-devices-by-using-the-aws-iot-credentials-provider/
* For further reading:
  * https://docs.aws.amazon.com/iot/latest/developerguide/authentication.html
  * AWS IoT Authentication deep-dive course: https://www.aws.training/Details/Curriculum?id=42335

### Communication
AWS IoT is built on top of the IoT standard MQTT protocol, and uses HTTPS for communication.
see protocols [docs](https://docs.aws.amazon.com/iot/latest/developerguide/protocols.html) for more info 
It also supports MQTT over WebSockets as described [here](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt-ws.html).

#### Message brokers
The way devices communicate with the backend is by publishing and subscribing to messages queues.
The message broker provides a secure mechanism for devices and AWS IoT applications to publish and receive messages from each other. You can use either the MQTT protocol over HTTPS or over WebSocket to publish and subscribe.
for more info [see](https://docs.aws.amazon.com/iot/latest/developerguide/iot-message-broker.html)

#### IoT policies
During the provisioning process, you create a cert and attach an IoT policy to it. IoT policies determine which operations a device can perform **in the AWS IoT data plane**.
Although they are similar in format, **they are NOT AIM policies**, and are unlimited, they also include versioning unlike AIM policies and are only attached to IoT certificates.
For example: Allow a device to subscribe and publish to certain topics.
https://docs.aws.amazon.com/iot/latest/developerguide/iot-policies.html

#### Rules 
Rules give your devices the ability to interact with AWS services. Rules are analyzed and actions are performed based on the MQTT topic stream. 

//TODO - FINISH

they provide message processing and integration with other AWS services. You can use an SQL-based language to select data from message payloads, and then process and send the data to other services, such as Amazon S3, Amazon DynamoDB, and AWS Lambda. You can also use the message broker to republish messages to other subscribers.

You can then perform actions according to the results of the rule analysis.

A simple example:

A device publishes messages to some topic: tenant-abc/audits, the message is in JSON format.
A rule is defines so: "SELECT * FROM tenant-abc/audits" which means that any incoming message will result in some action (you can write other queries with logic in them)
An action is defined to send this incoming message to Kinesis to further processing.
You can also set multiple actions and fan out the messages that are processed by the rules.



https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html


#### Jobs //TODO
#### SDKs //TODO

## Other AWS IoT Services - //TODO
* device shadow //TODO
* secure tunneling //TODO
* Device management //TODO
  * IoT analytics analysis //TODO
  * reports //TODO
  * device defender //TODO
  * Events
  * device mgmt
  * audit //TODO
  * Mitigation actions //TODO
* greengrass
