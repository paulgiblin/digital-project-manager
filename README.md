# digital-project-manager
DevNet Create 2018

The current digital transformation trend is largely about digitizing existing business processes. In this workshop you will code against the Cisco Spark API and create a "digital project manager" which you can integrate with your digital apps to provide project teams with robust live status updates!

We will discuss a bit of unorthodox software called "Digital Project Manager" as an example. The Digital Project Manager is part of a larger application that defines and monitors the status of Ethernet access switch migrations. Because the application knows about the state of the migration, it can be used to supplement the migration team. Often during a network move, a project manager will be awake in the middle of the night pestering onsite engineers for migration status to relay to project stake holders. This slows down work, and the data engineers return is almost certainly inaccurate. If we think outside the box, we can turn Spark into more than just a notification target, we can make it a realtime migration log, work completion time estimator and report delivery vehicle! Participants will be encouraged to think of and implement other novel uses for Cisco Spark APIs.

Setup - 10-15 minutes
=====
We will go through a quick setup, clone the workshop repo, and verify prerequisites (Python, django, napalm) are installed.

Solution Demo - 10-15 minutes
=====  
We will walk through a real world implementation of the digital project manager functionality as used in Presidio's Switch Port Mapper tool.

Hands-On Coding - 45-60 minutes
=====
We will walk through provisioning a bot and obtaining a token in Cisco Spark; Programmatically organizing users in Spark teams and spaces; Collecting data with native switch infrastructure APIs and Napalm; Scrubbing the data and getting it into a useful format; Controlling the flow of aggregated report data; Formatting the data for Cisco Spark; and Sending the information to Cisco Spark.

Conclusion and next steps - 5-10 minutes
=====
We will recap what was learned, and participants will be called to consider and share other ways they think this type of Cisco Spark interaction could be used.