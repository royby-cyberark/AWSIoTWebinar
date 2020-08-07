# AWS IoT Webinar - Using AWS IoT for Authenticating External Services

## Welcome

Welcome to the CyberArk "AWS IoT" Webinar. 
below you will find general description, links and most importantly, step-by-step which you can follow to recreate everything we did during the webinar. 
I hope you enjoy the webinar and if you have any questions feel free to open an issue here or DM me @RoyBenYosefTM on twitter.

## Intro

AWS IoT is a suite of services, designed to allow the provisioning and managing of IoT devices in a secure manner. It includes things like, provisioning, authentication, two-way communication, variety of SDKs, Groups, Monitoring, Analysis and much more.

## What Are We Going To Build?
We will use AWS IoT to allow our services which are external to AWS, access to our cloud platform and allow them to communicate with our backend securly. We will see that AWS IoT doesnt have to do with IoT neccessarily, because what is an IoT device if not a machine running Linux? (or windows, or whatever for that matter)

## The Scenario
We have a canary service deployed in our network. this service acts as a honey-pot, which exposes seemingly lucrative endpoints that appeal to attackers. for example RDP, SSH Servers, various databases and more. since these aren't real services, usually we wouldn't expect anyone to try to communicate with them, and so upon detecting such a connection attempt the canary service must inform us of this incident.

In our cloud platform, we run an audit service, and we would like the canary to report to it directly for each suspicious incident. To do this we much put in place secure authentication and authorization means, so the canary service can communicate with the backend securely.

We are going to use AWS IoT for this, since everything it provides can easily be used with any scenario and not necessarily with actual IoT devices.

But before we dive in, let's do a quick overview of the prominent services that AWS IoT has to offer.

## IoT Services and Features - overview

https://github.com/royby-cyberark/AWSIoTWebinar/blob/master/aws-iot-services.md

## AWS IoT Hands-on Session

https://github.com/royby-cyberark/AWSIoTWebinar/blob/master/aws-iot-hands-on.md

