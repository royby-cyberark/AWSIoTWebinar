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

**Prerequisites:**
* git
* python 3.7+

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
  * Details: arn, thing type - note your device arn for later
  * Security: review the certificate, its arn, policies and things
  * Groups
* Click on "Edit" in the thing page and add an attribute, which key is 'Owner' and value is abcde-12345. we will later use this is the policy that will restric devices to post to their teant topic

### Rule creation
* Create an S3 bucket
  * Open S3, create bucket, name it `iot-webinar-audits`
  * Use all defaults and create bucket
* Under "Act", "Rules", click "Create"
* Name it `IotWebinarRule` (only alphanumeric and underscore are allowed)
* Set the SQL query to `SELECT * FROM 'abcde-12345/+/audit'` (Use the default SQL version)  //TODO - fix this to use thing-name???
  This select the entire message from the topic that start with the tenant-id 'abcde-12345', then any path then 'audit'
  This, along with the policy restrictions will help us achieve tenant isolation.
  see [this](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-from.html) for more info about FROM clause wildcards 
* Create S3 store action
  * Click on "Add Action"
  * Select S3
  * Select the 'iot-webinar-audits' bucket and set the key to `${topic()}/${timestamp()}` see [this](https://docs.aws.amazon.com/iot/latest/developerguide/iot-substitution-templates.html) for details on substitution template
  * To create a role that will allow iot to access our S3 bucket: "Create Role" and name it `iot-webinar-s3-role` 
  * Click on "Add Action" to finalize the creation
* Create an SNS push notification action
  * "Add Action"
  * Under "SNS Topic" click "Create" and name it `iot-webinar-sns-topic`
  * To create a role that will allow iot to send SNS notifications: "Create Role" and name it `iot-webinar-sns-role`
  * Click on "Add Action" to finalize the creation
  * Subscribe to SNS notifications
    * Open the SNS service
    * Subscrption, Create subsription
    * Under "Topic ARN", use auto-complete to select your SNS webinar topic arn
    * Select "Email" for "Protocol"
    * For "Endpoint", enter your email and click "Create Subscription"
    * Open the email and click the confirm link
* Review your new roles
* "Create Rule"

### IoT Policy creation
* "Secure", "Policies", "Create", name it `iot-webinar-policy`
* Under "Add Statements". //TODO - verify minimum required actions
  * Add the following actions: `iot:Connect,iot:Receive,iot:Publish,iot:Subscribe` (the field uses auto-complete) 
  * Under 'Resource ARN' paste the device arn you noted before //TODO - what do we need here?
  * For "Effect", check "Allow"
  * "Create"
  
  
  
//TODO: FIX THIS:
* Go to thing, security, certificate, attach policy

actually use this (TODO FIX THIS):
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": "arn:aws:iot:eu-west-1:195361640859:client/${iot:Connection.Thing.ThingName}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "arn:aws:iot:eu-west-1:195361640859:topic/${iot:Connection.Thing.Attributes[Owner]}/${iot:Connection.Thing.ThingName}/audit"
    }
  ]
}
```

//TODO - see this: https://docs.aws.amazon.com/iot/latest/developerguide/thing-policy-variables.html
//TODO - see this: https://docs.aws.amazon.com/iot/latest/developerguide/example-iot-policies-elements.html
//TODO and examples: https://docs.aws.amazon.com/iot/latest/developerguide/pub-sub-policy.html, etc.

### Test the rule 
* Open "Act", "Tests"
* Under publish, enter iot/audit
* Click "Publish to topic"

//TODO - limit of rules, generally write the limits

### Cloudwatch logging 
* Open https://console.aws.amazon.com/cloudwatch/, choose "Log groups".
* In the Filter text box, enter `AWSIotLogsV2` , and then press Enter
* For more info, see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html)
* If you want to configure the logging vebosity, you can do that in the "Settings" page in the IoT dashboard

### Device Setup
* In the IoT dashboard, click on "settings" and note your service endpoint address
* //TODO - implement
* The IoT (and other) SDKs can be found here: 
  * SDK Hub: https://aws.amazon.com/tools/#sdk, under "IoT Device SDKs"
  * The Python SDK is here: https://github.com/aws/aws-iot-device-sdk-python
  * SDK code samples: https://github.com/aws/aws-iot-device-sdk-python
* `git clone git@github.com:royby-cyberark/AWSIoTWebinar.git`
* //TODO - venv, activate, pipinstall `pip install AWSIoTPythonSDK`, `pip install requests`
* Run the following command line, replacing all placeholders with your values:
`python canary-service.py -e <your iot endpoint> -r <path to root ca file - AmazonRootCA1.pem> -c <path to cert file - 8ad305037c-certificate.pem.crt> -k <path to private key file - 8ad305037c-private.pem.key> -id iot-webinar-device -t abcde-12345/iot-webinar-device/audit`

* Open http://localhost:80 (this is the so called honeypot), which will in turn, send an even audit message to the topic
* See that an audit was writter to the S3 bucket and also that an email notification was sent.

//TODO - tenantid/device name/type/group?

* //TODO - fix timeout, updated policy to "Resource": "arn:aws:iot:eu-west-1:195361640859:*", and then the client worked. fix this.

### Job creation
* Cert rotation...
* //TODO - this shouldn't be manual...


* Under 'Set searchable thing attributes' add a 'tenant_id' attribute and set its value to `abcdef-12345` //TODO - say something, where's the value?
* Click on "Next step" and except to get a "Successfully created thing." message
* 
