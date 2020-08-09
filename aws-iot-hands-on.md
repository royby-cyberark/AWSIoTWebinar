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

## Step-By-Step


