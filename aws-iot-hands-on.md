# AWS IoT Hands-On session

🔥🔥 **DISCLAIMER 1:** 🔥🔥

Using AWS costs money. while the things we do here may or may not be under the free tier (and even if not, they are very low volume), 
you are responsible for the costs and the resources you create and to clean up after yourself.
A Cleanup section is provided at the bottom, but it many contain mistakes, os make sure you clean up what you did after it is no longer needed and bear in mind the costs

---------------------

🔥🔥 **DISCLAIMER 2:** 🔥🔥

As webinars go, some of the settings here were simplified. when it come to production systems and code, you are responsible to do your own research and security review all parts including but not limited to IAM policies, IoT policies, certificates, S3 bucket settings and more.
Consider this a webinar grade material and treat it as such.

---------------------

Below you can find a step-by-step for our AWS IoT Webinar. 
A little reminder first:

## What Are We Going To Build?
We will use AWS IoT to allow our services which are external to AWS, access to our cloud platform and allow them to communicate with our backend securely. We will see that AWS IoT doesn't have to do with IoT necessarily, because what is an IoT device if not a machine running Linux? (or windows, or whatever for that matter)

## The Scenario
We have a honeypot service deployed in our network. this service is intended to lure attackers by exposing seemingly lucrative endpoints. For example RDP, SSH Servers, various databases, and more. since these aren't real services, usually we wouldn't expect anyone to try to communicate with them, and so upon detecting such a connection attempt the honeypot service must inform us of this incident.

In our cloud platform, we run an audit service, and we would like the honeypot to report to it directly for each suspicious incident. To do this we must put in place secure authentication and authorization means, so that the honeypot service can communicate with the backend securely.

We are going to use AWS IoT for this since everything it provides can easily be used with any scenario and not necessarily with actual IoT devices.

But before we dive in, let's do a quick overview of the prominent services that AWS IoT has to offer.


**A Note on Infrastructure as code:**

Being focused on the AWS IoT, I will go through the steps using the AWS console. in a real environment you will, of course, do things differently. 
For example, you will deploy all your resources with CDK (or another similar framework), keeping the producing code in source control. 
and have your infrastructure "as code".

I recommend watching our revious webinar on CDK: //TODO link

For full code examples, see the [SDK page](https://github.com/royby-cyberark/aws-iot-device-sdk-python)

## Step-By-Step

**Prerequisites:**
* git
* Python 3.7+
* The ability to create virtual environments and install packages (e.g. use venv and pip)

### Get the code
* `git clone git@github.com:royby-cyberark/AWSIoTWebinar.git`

----------------------------

### Device creation
* In the AWS Console, open the "AWS IoT Core" service
* Under "Manage", "Things", click on "Create"
* Click "Create a single thing"
* Name your device `iot-webinar-device`
* Optional: Click on "Create Type" and name it `iot-webinar-type` - this will create a device type that we can use later to group devices by type and act upon this type. You can use thing types to set properties that are shared for this type, and also use it as policy variables
* Under "Add this thing to a group", click "Create group" and name the group `iot-webinar-group`, click "Create", this will be used later during the jobs step
* Make sure your device group is set to the new group, click "Next" 
* Select "One-click certificate creation"
* On the next page, we are presented with a link to download the device certificate 
* Download the certificate, private key and optionally the public key and save them into the `AWSIoTWebinar/source` folder in the git repo folder you cloned, under the `source` folder
  * Save the certificate as `certificate.pem.crt` 
  * Save the private key as `private.pem.key`
  * Save the Root CA as `AmazonRootCA1.pem`
  * Strictly speaking, the public key is not required on our end. but you can use it in the bonus section at the bottom.
* You also need AWS's Root ca which you can find [here](https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html?icmpid=docs_iot_console#server-authentication-certs)
* We are going to download the "RSA 2048 bit" key, right-click on the link and save to file locally
* Click on "Activate", this will activate the certificate that you created and associated with the device.
* Click on "Attach policy" and **DO NOT** pick a policy (we will create a policy later)
* Click "Register thing"
* Under "Manage", "Things", open your device and review it
  * Details: arn, thing type - note your device arn for later
  * Security: review the certificate, its arn, policies, and things **note the certificate name for later use**
  * Groups
* Click on "Edit" in the thing page and add an attribute, which key is 'Owner', and value is `abcde-12345`. we will later use this is the policy that will restrict devices to post to their tenant topic

----------------------------

### Rule creation
* Create an S3 bucket
  * Open S3, create bucket, name it `iot-webinar-audits-<random stuff>` (S3 bucket names are globally unique)
  * Use all defaults and create bucket
* Under "Act", "Rules", click "Create"
* Name it `IotWebinarRule` (only alphanumeric and underscore are allowed)
* Set the SQL query to `SELECT * FROM 'abcde-12345/+/audit'` (Use the default SQL version) 
  This selects the entire message from the topic that starts with the tenant-id 'abcde-12345', then any path then 'audit'
  This, along with the policy restrictions will help us achieve tenant isolation.
  see [this](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-from.html) for more info about FROM clause wildcards 
  * You can also use thing name, type and other properties as policy variables, see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/iot-policy-variables.html)
* Create S3 store action
  * Click on "Add Action"
  * Select S3
  * Select the S3 bucket and set the key to `${topic()}/${timestamp()}` see [this](https://docs.aws.amazon.com/iot/latest/developerguide/iot-substitution-templates.html) for details on substitution templates
  * To create a role that will allow iot to access our S3 bucket: "Create Role" and name it `iot-webinar-s3-role` 
  * Click on "Add Action" to finalize the creation
* Create an SNS push notification action
  * "Add Action"
  * Under "SNS Topic" click "Create" and name it `iot-webinar-sns-topic`
  * To create a role that will allow iot to send SNS notifications: "Create Role" and name it `iot-webinar-sns-role`
  * Click on "Add Action" to finalize the creation
  * Subscribe to SNS notifications
    * Open the SNS service
    * Subscription, Create Subscription
    * Under "Topic ARN", use auto-complete to select your SNS webinar topic arn
    * Select "Email" for "Protocol"
    * For "Endpoint", enter your email and click "Create Subscription"
    * Open the email and click the confirm link
* Review your new roles
* "Create Rule"

**Note:** IoT rules are soft limited to 1000 per account, which means you can request an increase and expect to get at least 10x that, but this is specific to the service and the use case.

----------------------------

### IoT Policy Creation
* To create a policy open "Secure", "Policies", "Create", name it `iot-webinar-policy`
* Click on "Advanced mode" and paste the following policy document:
  
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

* Go to thing, security, certificate, attach policy

This policy allows a device (client) of the specified arn to connect. It requires the arn to include the specific thing name.
Also, it allows to publish only to a topic that starts with the device "Owner" attribute value followed by the device thing name, followed by "audit".
This allows us to reuse this policy for other devices. but you can create explicit policies if you choose to do so.

**NOTE:** IoT policies are not limited, for service quotas, see the [docs](https://docs.aws.amazon.com/general/latest/gr/iot-core.html#limits_iot)

To learn more about policy variables and some IoT policy examples, see:

https://docs.aws.amazon.com/iot/latest/developerguide/thing-policy-variables.html
https://docs.aws.amazon.com/iot/latest/developerguide/example-iot-policies-elements.html
https://docs.aws.amazon.com/iot/latest/developerguide/pub-sub-policy.html

### Test the rule 
* Open "Act", "Tests"
* Under publish, enter iot/audit
* Click "Publish to topic"

----------------------------

### Cloudwatch logging 
* Open https://console.aws.amazon.com/cloudwatch/, choose "Log groups"
* In the Filter text box, enter `AWSIotLogsV2`, and then press Enter
* For more info, see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html)
* If you want to configure the logging verbosity, you can do that in the "Settings" page in the IoT dashboard

----------------------------

### Device Setup
* In the IoT dashboard, click on "settings" and note your service endpoint address
* The IoT (and other) SDKs can be found here: 
  * SDK Hub: https://aws.amazon.com/tools/#sdk, under "IoT Device SDKs"
  * The Python SDK is here: https://github.com/aws/aws-iot-device-sdk-python
  * SDK code samples: https://github.com/aws/aws-iot-device-sdk-python
* Set up your python virtual env (this may vary according to you os and the way you do virtual environments)
  * Open a terminal and run the following commands:
  * `python -m venv .venv
  * `source .venv/bin/activate` (on windows you need to run the activate batch file)
  * `pip install AWSIoTPythonSDK requests`
* Run the following command line, replacing the endpoint placeholder with your endpoint address:
`python canary-service.py -e <your iot endpoint> -r AmazonRootCA1.pem -c certificate.pem.crt -k private.pem.key -id iot-webinar-device -t abcde-12345/iot-webinar-device/audit`
  * `-e` is your IoT service endpoint which you notes before (from the settings page)
  * `-id` is the client id, it is up to you, but it is recommended to use the thing name
  * `-t` is the topic we will publish to

* Open http://localhost:80 (this is the so-called honeypot), which will, in turn, send an incident audit message to the topic
* See that an audit was written to the S3 bucket and also that email notification was sent

----------------------------
----------------------------

### Job creation
We are going to create a job for certificate rotation. we will provide the certificate as a pre-signed url in S3 which will be short-lived.

* In S3, open your bucket
  * Create a folder named `jobs` and optionally select "AES-256 (SSE-S3)" for encryption (this is beyond the scope of this webinar, but why not)
  * Open the `jobs` folder and create a sub-folder named `certs`, also with SSE-S3 encryption

* In the IoT dashboard, under "Manage", click on "Jobs", "Create Custom Job"
* Set the job id to `webinar-job-rotate-cert`
* Under "Select devices to update", either select your device (iot-webinar-device), or its group (iot-webinar-group). Using groups will allow us to apply this job to multiple devices.
* Create the job document file. this needs to be uploaded to S3, alternatively, you can use things like aws cli, boto3, etc, and avoid the need to create an S3 object.
  * TODO - from repo folder - two files!, Create a local file named `job-rotate-cert.json`, paste this into it and save it locally.
  //TODO - explain the fields
  * Upload the files to our S3 bucket, under the `jobs` folder.
* //TODO - order these items
* Back in the job creation, under "Add a job file", navigate to `job-rotate-cert.json` and select it
* Select "I want to pre-sign my urls..."
* Click "Create role" and name it `iot-webinar-signedurls-role`, review this role and policy to understand what was done
* Click "Next", "Create"
* Replace the thing policy with the following (//TODO - step by step):

```{
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
        "iot:Publish",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:eu-west-1:195361640859:topic/${iot:Connection.Thing.Attributes[Owner]}/${iot:Connection.Thing.ThingName}/audit",
        "arn:aws:iot:eu-west-1:195361640859:topic/$aws/things/${iot:Connection.Thing.ThingName}/jobs/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": "arn:aws:iot:eu-west-1:195361640859:topicfilter/$aws/things/${iot:Connection.Thing.ThingName}/jobs/*"
    }
  ]
}
```

* Command: `python jobs-handler.py -e <your iot endpoint> -r AmazonRootCA1.pem -c certificate.pem.crt -k private.pem.key -id iot-webinar-device -n iot-webinar-device`
  * `-n` is the thing name that will subscribe to the jobs topic

//TODO - move this up. create sub header for the next parts
#### Create a simple job
* Under "Manage", "Jobs", "Create", "Create Custom Job"
* Job id = `local-scan-job-01`
* Under devices to update, select your device (you can also select the device group to update all group members)
* Under "Add a job file", select `job-local-scan.json` from our S3 bucket
* Click on "Next", "Create"
* Alternatively, you can create a job with the cli:
```
aws iot create-job \
              --job-id "local-scan-job-01" \
              --targets "arn:aws:iot:eu-west-1:<account_id>:thing/<thing_name>" \
              --document file://job-local-scan.json \
              --description "example status job" \
              --target-selection SNAPSHOT
```
And delete the job with:
`aws iot delete-job --job-id "status-job-01"`

#### Create a cert rotation job:
* First, create the new secrets
  * "Manage", "Things", select our device `iot-webinar-device`
  * "Security", "Create certificate"
  * Download the certificate, private key, and optionally the public key and save them into **ANOTHER** folder. This will be done on a different machine. make sure you don't save those into the project folder.
    * Strictly speaking, the public key is not required on our end. but you can use it in the bonus section at the bottom.
  * Click "Activate"
  * Click "Attach Policy", select our policy `iot-webinar-policy` and click "Done"
  * Open the thing, security page and **note the new certificate name for later**
* Upload the new certificate and private key into our S3 bucket under the `certs` folder
  * Upload the certificate as `certificate.pem.crt` 
  * Upload the private key as `private.pem.key`
* "Manage", "Jobs", "Create", "Create custom job"
* Job id = `webinar-rotate-cert-01`
* Under devices to update, select your device (you can also select the device group to update all group members)
* Under "Add a job file", select `job-rotate-cert.json` from our S3 bucket
* Under "Pre-sign resource URLs", select "I want to pre-sign my URLs and have configured my job file."
  * Take a look at `job-rotate-cert.json`, this will have the IoT service replace the presigned url placeholders with real values.
* When using presigned urls, you **must** use a role that will allow you access to the bucket, pick the `iot-webinar-signedurls-role` role
* Click on "Next", "Create"
* See that you got the job and rotated the files locally
* Send another local-scan job to ensure that the connection is working
* Deactivate the old certificate
  * "Manage", "Things", select `iot-webinar-device`, "Security"
  * Click on the old cert (according to the name you noted at the beginning)
  * "Actions", "Deactivate"
* Send another local-scan job to ensure that the connection is working
* Deactivate the new cert
* TODO - explain about revoking certs and connected devices - https://forums.aws.amazon.com/thread.jspa?threadID=225768

* You can always create jobs with the cli:
```
aws iot create-job \
              --job-id "local-scan-job-01" \
              --targets "arn:aws:iot:eu-west-1:<account_id>:thing/<thing_name>" \
              --document file://job-local-scan.json \
              --description "example status job" \
              --target-selection SNAPSHOT
``` 
And delete the job with:
`aws iot delete-job --job-id "local-scan-job-01"`

* Create a cert rotation task from the cli:
```
aws iot create-job \
              --job-id "rotate-job-01" \
              --targets "arn:aws:iot:eu-west-1:<account_id>:thing/<thing_name>" \
              --document file://job-rotate-cert.json \
              --description "example cert rotation job" \
              --target-selection SNAPSHOT \
              --presigned-url-config roleArn=<role_arn>,expiresInSec=300
```

* In a real process, you would wait for the jobs to be completed and then remove the old certificate
  * You can see the job status by calling //TODO

* For a full code example, see the [SDK code sample](https://github.com/royby-cyberark/aws-iot-device-sdk-python/blob/master/samples/jobs/jobsSample.py)


### Bonus stuff 1 - augmenting data with tenant id
You can augment the message that is passed for example to S3, with data from the topic path. 
This can be useful, for example, if you include the tenant id in the topic, you can augment that data with its value. 
Update your Rule SQL query to something similar to this:
`SELECT message as msg, topic(1) as tenant_id FROM ‘+/audit’`
Now, look at the data that goes into the S3 bucket and see how it's changed.
//TODO - test this

### Bonus stuff 2 - encrypting your certs with asymmetric encryption
Even though presigned urls are generally safe and can be set to expire after some time, still, anyone with the link can download the files that it points to.
<BR>
You can, if you want to secure your secrets better, use asymmetric encryption with the public key that is provided to you for the device cert.

* When creating the certificate, make sure you get the public key and store it somewhere that is accessible to the process that does the rotation. 
public keys are no secret, so you don't have to worry about it too much, just keep it accessible by thing name (maybe a DynamoDB table for key-value)
* During the rotation process, encrypt the files with the public key
* The device handling the job can use its private key to decrypt it
* You can, for example, indicate that it is encrypted in the job body 

Below you can find sample python code for doing the encryption/decryption using the public/private keys, but keep in mind that this is sample code
and as such should not be used in production as-is.
//TODO - test this
Asymmetric crypto sample:
https://github.com/royby-cyberark/AWSIoTWebinar/blob/master/sample/sample-asymmetric-crypto.py


### Cleaning up
Delete all resources you created, this should be the list of them, but please verify this yourself.
//TODO - verify this
* Delete thing: iot-webinar-device
* Delete type: iot-webinar-type
* Delete group: iot-webinar-group
* Delete policy
* Delete rule
* Delete Job
* Delete cert: 8ad305037c.cert.pem	
* Delete S3 bucket (first delete all files and folders)
* //TODO find all "created" roles during the process - search roles for webinar (other?)
  * delete role `iot-webinar-signedurls-role`

//TODO - something else>
