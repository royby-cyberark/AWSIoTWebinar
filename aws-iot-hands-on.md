# AWS IoT Hands-On session

💵💵 **DISCLAIMER 1:** 💵💵

Using AWS costs money. while the things we do here may or may not be under the free tier (and even if not, they are very low volume), 
you are responsible for the costs and the resources you create and to clean up after yourself.
A Cleanup section is provided at the bottom, but it many contain mistakes, os make sure you clean up what you did after it is no longer needed and bear in mind the costs

---------------------

🔥🔥 **DISCLAIMER 2:** 🔥🔥

As webinars go, some of the settings here were simplified. when it come to production systems and code, you are responsible to do your own research and security review all parts including but not limited to IAM policies, IoT policies, certificates, S3 bucket settings and anything else that is mentioned here.
Consider this a webinar grade material and treat it as such.

Especially note all default role creation, in a real scenario, you must review and narrow down your policies to the absolute minimus needed.

---------------------


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
I recommend watching our [previous webinar on CDK](https://www.youtube.com/watch?v=W7rF62a96G0)

For full code examples, see the [SDK page](https://github.com/aws/aws-iot-device-sdk-python)


# Step-By-Step

**Prerequisites:**
* git
* Python 3.7+
* The ability to create virtual environments and install packages (e.g. use venv and pip)


## Get the Code
* `git clone git@github.com:royby-cyberark/AWSIoTWebinar.git`

 
## Device Creation

* In the AWS Console, open the "AWS IoT Core" service
* Under "Manage", "Things", "Register a thing" (Or "Create" if you already have devices)
* Click "Create a single thing"
* Name your device `iot-webinar-device`
* Optional: Click on "Create Type" and name it `iot-webinar-type` - this will create a device type that we can use later to group devices by type and act upon this type. You can use thing types to set properties that are shared for this type, and also use it as policy variables
* Under "Add this thing to a group", click "Create group" and name the group `iot-webinar-group`, click "Create", this will be used later during the jobs step
* Add an attribute, which key is `Owner`, and value is `abcde-12345`. we will later use this is the policy that will restrict devices to post to their tenant topic
* Make sure your device group is set to the new group, click "Next" 
* Select "One-click certificate creation"
  * If this is the first time you're using AWS IoT you might get an error 
    >We are provisioning a Device Gateway endpoint for your account. It may take a few minutes for the endpoint to be ready, after which you can connect devices   to AWS IoT, publish/subscribe to topics, and access device shadows.
  
  in this case, either wait, or try to open the thing page from the "Manage" side link, go to "Security" and create the certificate from there.
* On the next page, we are presented with a link to download the device certificate 
* Download the certificate, private key and optionally the public key (for the bonus section) and save them into the `AWSIoTWebinar/source` folder in the git repo folder you cloned, under the `source` folder
  * Save the certificate as `certificate.pem.crt` 
  * Optionally save the public key as `public.pem.key`
  * Save the private key as `private.pem.key`
  * Save the Root CA as `AmazonRootCA1.pem` (download the "RSA 2048 bit" key from [here](https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html?icmpid=docs_iot_console#server-authentication-certs), right-click on the link and save to file locally)
  * Strictly speaking, the public key is not required on our end. but you can use it in the bonus section at the bottom.
* Click on "Activate", this will activate the certificate that you created and associated with the device.
* Click on "Done" (or "Attach policy" and "Done) but **DO NOT** pick a policy (we will create a policy later)
* Click "Register thing"
* Under "Manage", "Things", open your device and review it
  * Details: arn, thing type - note your device arn for later
  * Security: review the certificate, its arn, policies, and things **note the certificate name for later use**
  * Groups


## Rule Creation

* Create an S3 bucket
  * Open S3, create bucket, name it `iot-webinar-audits-<random stuff>` (S3 bucket names are globally unique)
* Under "Act", "Rules", click "Create"
* Name it `IotWebinarRule` (only alphanumeric and underscore are allowed)
* Set the SQL query to `SELECT * FROM 'abcde-12345/+/audit'` (Use the default SQL version) 
  
  This selects the entire message from the topic that starts with the tenant-id 'abcde-12345', then any path, then 'audit'
  
  This, along with the policy restrictions will help us achieve tenant isolation.
  see [this](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-from.html) for more info about FROM clause wildcards 
  * You can also use thing name, type and other properties as policy variables, see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/iot-policy-variables.html)
* Create S3 store action
  * Click on "Add Action"
  * Select S3, "Configure action"
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
    * Under "Topic ARN", use auto-complete to select your SNS webinar topic arn (for `iot-webinar-sns-topic`) 
    * Select "Email" for "Protocol"
    * For "Endpoint", enter your email and click "Create Subscription"
    * Open the email and click the confirm link
* Review your new roles
* "Create Rule"

**Note:** 
IoT rules are soft limited to 1000 per account, which means you can request an increase and usually expect to get at least 10x that, but this is specific to the service and the use case.

## IoT Policy Creation

* To create a policy open "Secure", "Policies", "Create", name it `iot-webinar-policy`
* Click on "Advanced mode" and paste the following policy document:
  
**IMPORTANT!** Replace the region and account placeholders with your values for region and account number (best to take it from the policy arn which will minimize the chance of a mistake)
  
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": "arn:aws:iot:<region>:<account>:client/${iot:Connection.Thing.ThingName}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "arn:aws:iot:<region>:<account>:topic/${iot:Connection.Thing.Attributes[Owner]}/${iot:Connection.Thing.ThingName}/audit"
    }
  ]
}
```

* "Create"
* Open our "thing" from the "Manage" page, go to "Security", "Certificate", click on the certificate, "Action", then "Attach policy"

This policy allows a device (client) of the specified arn to connect. It requires the arn to include the specific thing name.
Also, it allows to publish only to a topic that starts with the device "Owner" attribute value followed by the device thing name, followed by "audit".
This allows us to reuse this policy for other devices. but you can create explicit policies if you choose to do so.

**NOTE:** 
IoT policies are not limited, for service quotas, see the [docs](https://docs.aws.amazon.com/general/latest/gr/iot-core.html#limits_iot)

To learn more about policy variables and some IoT policy examples, see:

https://docs.aws.amazon.com/iot/latest/developerguide/thing-policy-variables.html
https://docs.aws.amazon.com/iot/latest/developerguide/example-iot-policies-elements.html
https://docs.aws.amazon.com/iot/latest/developerguide/pub-sub-policy.html


## Cloudwatch Logging 

* If you want to turn on logging, go to "settings", turn it on and select the desired log level
  * Create a role for writing to CloudWatch and name it `iot-webinar-logs`
* Open https://console.aws.amazon.com/cloudwatch/, choose "Log groups"
* In the Filter text box, enter `AWSIotLogsV2`, and then press Enter (It might be `AWSIotLogs` if your region does not support `AWSIotLogsV2` yet)
* For more info, see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html)
* If you want to configure the logging verbosity, you can do that in the "Settings" page in the IoT dashboard
iot-webinar-logs


## Device Setup

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


## Jobs

We are going to create a job for certificate rotation. we will provide the certificate as a pre-signed url in S3 which will be short-lived.

### Policy Update

First let's update the policy so we can subscribe to the jobs topics, public and read from them.

* "Secure", "Policies", open `iot-webinar-policy`, "Edit policy document"
* Paste the following policy document:

**IMPORTANT!** Replace the region and account placeholders with your values for region and account number (best to take it from the policy arn which will minimize the chance of a mistake)
  

```{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": "arn:aws:iot:<region>:<account>:client/${iot:Connection.Thing.ThingName}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:<region>:<account>:topic/${iot:Connection.Thing.Attributes[Owner]}/${iot:Connection.Thing.ThingName}/audit",
        "arn:aws:iot:<region>:<account>:topic/$aws/things/${iot:Connection.Thing.ThingName}/jobs/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": "arn:aws:iot:<region>:<account>:topicfilter/$aws/things/${iot:Connection.Thing.ThingName}/jobs/*"
    }
  ]
}
```

This policy will allow us to:
1. Connect as before
2. Public and receive messages on the audit topic (like before) - isn't used in the jobs example
3. Public and receive messages on the reserved topic for jobs topic.
4. Subscribe to the reserved topic for jobs topic filter.

Notes:
* The topic for jobs is reserved by aws and it has the following format: $aws/things/thingName/jobs/get. for more information see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html)
* To be able to work with jobs, you must subscribe to the topicfilter. the reason for this is that being pub-sub, a client can publish to one topic (at a time), but subscribe to multiple topics. this is done by using the wildcard supporting topicfilter for subscribing and the non-wildcard-supporting topic for publishing and receiving. see the [doc](https://docs.aws.amazon.com/iot/latest/developerguide/topics.html#topicfilters).


### S3 Bucket Setup

* In S3, open your bucket
  * Create a folder named `jobs` and optionally select "AES-256 (SSE-S3)" for encryption (this is beyond the scope of this webinar, but why not)
  * Open the `jobs` folder and create a sub-folder named `certs`, also with SSE-S3 encryption

We will use these folders to keep the new certificate and job files respectively


### Prepare Job Files

* Review and upload job files
  * Jobs are described in json files. they can be either provided from an S3 bucket if you're using the console, local file for the cli or string for the sdk
  * Upload `job-rotate-cert.json` and `job-local-scan.json` to the S3 bucket under `jobs`
  * You can put anything you want there and have the device receive it. 
  * If you would like to serve presigned urls for S3 files, you need to use the presigned placeholders in the following format `${aws:iot:s3-presigned-url:<s3 url>}`, see example in `job-rotate-cert.json`
  
  For more info on presigned urls for jobs see the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/create-manage-jobs.html)


### Running our Program 

Don't forget to replace iot endpoint with your endpoint address
* Run: `python jobs-handler.py -e <your iot endpoint> -r AmazonRootCA1.pem -c certificate.pem.crt -k private.pem.key -id iot-webinar-device -n iot-webinar-device`
  * `-n` is the thing name that will subscribe to the jobs topic

We are now connected and waiting for jobs.


### Create a Simple Job

* Under "Manage", "Jobs", "Create", "Create Custom Job"
* Set bob id to `local-scan-job-01`
* Under "Devices to update", select your device (you can also select the device group to update all group members)
* Under "Add a job file", select `job-local-scan.json` from our S3 bucket
* Click on "Next", "Create"
* Alternatively, you can create a job with the cli (run from the `source` folder or point to the json file in another folder):
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

* See that the job client receives the created job.


### Create a Certificate Rotation Job:

* First, create the new secrets
  * "Manage", "Things", select our device `iot-webinar-device`
  * "Security", "Create certificate"
  * Download the certificate, private key, and optionally the public key and save them into **ANOTHER** folder. In a real environment, this will usually not be done on a different machine. make sure you don't save those into the project folder.
    * Strictly speaking, the public key is not required on our end. but you can use it in the bonus section at the bottom.
  * Click "Activate"
  * Click "Attach Policy", select our policy `iot-webinar-policy` and click "Done"
  * Open the thing, security page and **note the new certificate name for later**
* Upload the new certificate and private key into our S3 bucket under the `certs` folder
  * Upload the certificate as `certificate.pem.crt` 
  * Upload the private key as `private.pem.key`
* "Manage", "Jobs", "Create", "Create custom job"
* Set the job id to `webinar-rotate-cert-01`
* Under devices to update, select your device (you can also select the device group to update all group members)
* Under "Add a job file", select `job-rotate-cert.json` from our S3 bucket
* Under "Pre-sign resource URLs", select "I want to pre-sign my URLs and have configured my job file"
  * Take a look at `job-rotate-cert.json`, this will have the IoT service replace the presigned url placeholders with real values.
* When using presigned urls, you **must** use a role that will allow you access to the bucket
  * If this is the first time click "Create role" and name it `iot-webinar-signedurls-role`, review this role and policy to understand what is done
  * If you already created the role, simply select it
* Click on "Next", "Create"
* See that you got the job and rotated the files locally (you can look at the console output and the file update time)
* The client has now reconnected with the new certificate and the old certificate can be revoked. 

**NOTE:** 
When testing it is better to deactivate the certs so you can easily reactivate them when needed and not have to get them to the device again.


### Testing the Rotation 

**Note about Certificate Revocation:**
Due to the distributed architecture of the IoT service, the devices that are connected are not disconnected immediately when a certificate is revoked. 
if there are any changes to the certificate it will take a few minutes for them to be propagated across all the different nodes of the service and it will eventually reach the node where your device is currently connected and you should get a connection error.
This is documented in the UpdateCertificate API [docs](https://docs.aws.amazon.com/iot/latest/apireference/API_UpdateCertificate.html).
>“Within a few minutes of updating a certificate from the ACTIVE state to any other state, AWS IoT disconnects all devices that used that certificate to connect. >Devices cannot use a certificate that is not in the ACTIVE state to reconnect.”

//TODO - test this, test policy update

Since we don't want to wait "a few minutes" between each test, the easiest way to test this is simply restarting our program. 

**NOTE:** Since we are testing, I will deactivate the certificates instead of revoking them. this will have the exact same effect, but allow me to reactivate them again later without having to create another certificate and copy it to the device. 
In a real-world situation, you would revoke them. 

* Revoke the old certificate
  * "Manage", "Things", `iot-webinar-device`, "Security"
  * Click on the old certificate, use the name you noted before when creating it
  * Under "Actions", click "Deactivate" (or "Revoke" if you sure it is no longer needed)
* Terminal and run our jobs client
* Send a simple "local-scan-job" like before (See command line below)
* Verify that the job was received by the client
* Deactivate (or revoke) the new certificate
* Terminal and run our jobs client
* You are not able to connect this time

* Creating a local-scan job command:
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

* Create a cert rotation task command:
```
aws iot create-job \
              --job-id "rotate-job-01" \
              --targets "arn:aws:iot:eu-west-1:<account_id>:thing/<thing_name>" \
              --document file://job-rotate-cert.json \
              --description "example cert rotation job" \
              --target-selection SNAPSHOT \
              --presigned-url-config roleArn=<role_arn>,expiresInSec=300
```

A few more notes about jobs:

* In a real-world scenario, you would wait for the jobs to be completed and then remove the old certificate
  * You can see the job status by using the SDK or CLI for describing the job execution (e.g. `aws iot describe-job-execution`)

* For a full example, see the [SDK code sample](https://github.com/royby-cyberark/aws-iot-device-sdk-python/blob/master/samples/jobs/jobsSample.py)

* Jobs have a full life-cycle that we didn't go into, like job status, cancellation, rollout control, and more.
For more info see, as always, the [docs](https://docs.aws.amazon.com/iot/latest/developerguide/iot-jobs.html)


## Bonus Stuff

### Bonus Stuff 1 - Augmenting Data with Tenant-id

You can augment the message that is passed for example to S3, with data from the topic path. 
This can be useful, for example, if you include the tenant id in the topic, you can augment that data with its value. 
Update your Rule SQL query to something similar to this:

`SELECT message as msg, topic(1) as tenant_id FROM ‘+/audit’`

Now, look at the data that goes into the S3 bucket and see how it's changed.
//TODO - test this

See [this reference](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-functions.html) for functions that you can use in the query statement.
Which is under the [AWS IoT SQL reference](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-reference.html)


### Bonus Stuff 2 - Encrypting your Certificates with Asymmetric Encryption

Even though presigned urls are generally safe and can be set to expire after some time, still, anyone with the link can download the files that it points to.
<BR>
You can, if you want to secure your secrets further, use asymmetric encryption with the public key that is provided to you for the device cert.

* When creating the certificate, make sure you get the public key and store it somewhere that is accessible to the process that does the rotation. 
public keys are no secret, so you don't have to worry about it too much, just keep it accessible by thing name (maybe a DynamoDB table for key-value)
* During the rotation process, encrypt the files with the public key
* The device handling the job can use its private key to decrypt it
* You can, for example, indicate that it is encrypted in the job body 

Below you can find sample python code for doing the encryption/decryption using the public/private keys, but keep in mind that this is sample code
and as such should not be used in production as-is.

If you want to try this, do the following (may change due to os or the way you do virtual envs):
* Open a new terminal window (new virtual environment for python) 
* `python -m venv .venv`
* ` source .venv/bin/activate` (or run the batch in Windows)
* `pip install pycrypto`
* Run the encrypt script (replace placeholders with files): `python asymm-encrypt-sample.py -t <file to encrypt> -p <public key to encrypt with>`
* A new file name `enc_<file to encrypt>` is created. review its encrypted content
* Run the decrypt script: `python asymm-decrypt-sample.py -e <encrypted file> -p <private key to decrypt with>`
* A new 'dec_<encrypted file>' with the decrypted content is created
* Compare the original file with the decrypted file and rejoice with the equal content 

Asymmetric crypto code sample:

https://github.com/royby-cyberark/AWSIoTWebinar/blob/master/sample/sample-asymmetric-crypto.py


## Cleaning Up

Delete all resources you created, they may cost you and you shouldn't leave unused resources.
**IMPORTANT!** This list may not be complete or may have mistakes, you are responsible to clean us everything you created.

//TODO - verify this
* Deprecate the thing type: `iot-webinar-type` (You need to deprecate first, then wait 5 minutes, then delete it - all from the type, actions menu)
* From the thing page, "Security", delete all certificates
* Delete thing: 'iot-webinar-device'
* Delete group: 'iot-webinar-group'
* Delete policy (requires deleting the versions first)
  * Open the `iot-webinar-policy` policy
  * Delete the policy versions
  * Delete the policy (requires deletion of versions first)
* Delete Rule: `IotWebinarRule`
* Delete all Jobs	
* Delete S3 bucket
  * Delete all files and folders
  * Delete bucket
* Open the IAM service and delete all policies and roles:
  * Open "Roles"
  * Search for `webinar` (Assuming you adhered to the values in this guide)
  * For each of our roles (`iot-webinar-s3-role`, `iot-webinar-signedurls-role`, `iot-webinar-sns-role`, `iot-webinar-logs`)
    * Go to the policy under the "Permissions" tab and delete the policy
    * Delete the role
* Delete the `iot-webinar-type` thing type (assuming it has been 5 minutes)
* Delete the `iot-webinar-sns-topic` topic under SNS
  * TODO - check that subsription is deleted
