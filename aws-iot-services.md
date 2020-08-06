# AWS IoT Services and Features

## AWS IoT Core
The core service AWS IoT has to offer which we will focus on.

### Onboarding
One or more "Thing" provisioning. This includes creatoin and registration of a device, or "thing", download of the SDK that fits your needs, and setting some thing meta data, like thing type and attributes.

### Management
* Thing types - ease mangement by giving devices the same type and set of properties 
* Static groups - group things together which allows managing multiple things at once
* Dynamic groups - group based on device state which can change, for example, can be used to update devices that are with 80% battery or more
* Client Authentication
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
* message brokers //TODO
* Protocols //TODO
* IoT policies //TODO
* Rules //TODO
* Jobs //TODO
* SDKs

## Other AWS IoT Services
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
