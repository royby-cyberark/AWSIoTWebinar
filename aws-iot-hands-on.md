# AWS IoT Hands-On session

Below you can find a step-by-step for our AWS IoT Webinar. 
A little remider first:

## What Are We Going To Build?
We will use AWS IoT to allow our services which are external to AWS, access to our cloud platform and allow them to communicate with our backend securly. We will see that AWS IoT doesnt have to do with IoT neccessarily, because what is an IoT device if not a machine running Linux? (or windows, or whatever for that matter)

## The Scenario
We have a canary service deployed in our network. this service acts as a honey-pot, which exposes seemingly lucrative endpoints that appeal to attackers. for example RDP, SSH Servers, various databases and more. since these aren't real services, usually we wouldn't expect anyone to try to communicate with them, and so upon detecting such a connection attempt the canary service must inform us of this incident.

In our cloud platform, we run an audit service, and we would like the canary to report to it directly for each suspicious incident. To do this we much put in place secure authentication and authorization means, so the canary service can communicate with the backend securely.

We are going to use AWS IoT for this, since everything it provides can easily be used with any scenario and not necessarily with actual IoT devices.

But before we dive in, let's do a quick overview of the prominent services that AWS IoT has to offer.

**A Note Infrastructure as code**
Being focused on the AWS IoT, I will go through the steps using the AWS console. in a real environment, you will, of course, do thing differently. 
For example, you will deploy all your resources with CDK (or another similar framework), keeping the producing code in source control. 
and have your infrastructure "as code".


## Step-By-Step

### Device creation
* In the AWS Console, open the "AWS IoT Core" service
* Under "Manage", "Things", clicn on "Create"
* Click "Create a single thing"
* Name your device `iot-webinar-device`
* Optional: Click on "Create Type" and name it `iot-webinar-type` - this will create a device type which we can use later to group devices by type and act upon this type. //TODO add here - what are we doing with it
* Optional: under "Add this thing to a group", click "Create group" and name the group `iot-webinar-group`, click "Create" //TODO - what is this used for
* Make sure your device group is set to the new group, click "Next" 
* Select "One-click certificate creation"
* On the next page we are presented with a link to download the device certificate 
* Download the certificate, public key and private key
* You also need AWS's Root ca which you can find [here](https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html?icmpid=docs_iot_console#server-authentication-certs)
* We are going to download the "RSA 2048 bit" key, right click on the link and save to file locally
* Click on "Activate", this will activate the certificate that you created and associated with the device.
* Click on "Attach policy" and **DO NOT** pick a policy (we will create a policy later)
* "Register thing"
* Under "Manage", "Things", open your device and review it
  * Details: arn, thing type
  * Security: review the certificate, its arn, policies and things
  * Groups

### Rule creation
// * create rule - type? group? 
// * create policy
//   * policy variables group, attribute, type

### Job creation

###




**NOTE:** The device should have Python and Git (Optional) installed and a TCP connection to the public internet on port 8883


* Under 'Set searchable thing attributes' add a 'tenant_id' attribute and set its value to `abcdef-12345` //TODO - say something, where's the value?
* Click on "Next step" and except to get a "Successfully created thing." message
* 
