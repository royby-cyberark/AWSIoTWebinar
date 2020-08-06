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
You use an SQL syntax to act on those message, as shown below.
In simple words, devices can send messages to AWS IoT backend topics and you can use these messages to do things like: 

* Augment or filter data received from a device
* Write data received from a device to an Amazon DynamoDB database.
* Save a file to S3 
* Send a push notification to all users using Amazon SNS.
* Send a message to SQS
* Send messages to Kinesis
* Invoke a lambda
* Send data to the Amazon Elasticsearch Service.
* And more...

A simple example:

A device publishes messages to some topic: my-service/audits, the message is in JSON format.
A rule is defines so: "SELECT * FROM my-service/audits" which means that any incoming message will result in some action
An action is defined to send this incoming message to Kinesis to further processing.
You can also set multiple actions and fan out the messages that are processed by the rules.

https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html


#### Jobs
A job is a remote operation that is sent to and executed on one or more devices connected to AWS IoT. For example, you can define a job that instructs a set of devices to download and install application or firmware updates, reboot, rotate certificates, or perform remote troubleshooting operations.
In simple words, you can publish a job message to one or more devices, which in turn will recieve then and act upon it. 
An example would be creating a job to instruct a device to rotate its certificate.


### SDKs

AWS Provides a large number of SDKs for all major languages and platforms. 
You have an easy way to write client code on virtually any platform, but since it is also MQTT, you can also do things yourself, if you choose to do so.

* C++
  * C++ 11 or higher
  * CMake 3.1+
  * Clang 3.9+ or GCC 4.4+ or MSVC 2015+
* Java
* Python
* JS
* Embeded c
* Android
* iOS
* Arduino 

### Other AWS IoT Service

We will only mention those by name since they are generally out of scope for this webinar:

* Secure tunneling - When devices are deployed behind restricted firewalls at remote sites, you need a way to gain access to those device for troubleshooting, configuration updates, and other operational tasks.
* Device management
  * IoT analytics - a fully-managed service that makes it easy to run and operationalize sophisticated analytics on massive volumes of IoT data.
  * Device defender - a fully managed service that helps you secure your fleet of IoT devices. AWS IoT Device Defender continuously audits your IoT configurations to make sure that they aren’t deviating from security best practices.
  * Events - enables you to monitor your equipment or device fleets for failures or changes in operation, and to trigger actions when such events occur. 
* Greengrass - AWS IoT Greengrass is software that lets you run local compute, messaging, management, sync, and ML inference capabilities on connected devices in a secure way. With AWS IoT Greengrass, connected devices can run AWS Lambda functions, Docker containers, or both, execute predictions based on machine learning models, keep device data in sync, and communicate with other devices securely – even when not connected to the Internet.

And there's a lot more. I encourage you to go and see for yourself.
