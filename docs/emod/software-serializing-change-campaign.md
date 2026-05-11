# Changing serialized campaign parameters



Campaigns are used to distribute interventions to the people in the scenario.  When it comes to
serialization, only the interventions that have already been distributed to people are  serialized.
For example, if you are distributing drugs to people when they exhibit clinical symptoms, then
people who exhibited symptoms before the file was serialized should have their drugs. However, to
get drugs to the people exhibiting symptoms after reading from the serialized file, you will need to
add the campaign events that do that distribution.


The following overview is intended as high-level guidance for what changes can and cannot be made.


## Campaign events & event coordinators


See [Event coordinators](parameter-campaign-event-coordinators.md) for more information on events and event
coordinators.

### Events


Campaign events are not serialized.

### Event coordinators


Event coordinators are not serialized.  Any coordinator that was periodically distributing interventions
will need to be added to the new campaign.


## Interventions


### Node-level interventions


Node-level interventions are not serialized.  Any node-level vector control will need to be
redistributed.  Any **NodelLevelHealthTriggeredIV** that is responding to events will also need to be
redistributed.


### Individual-level interventions


Some individual-level interventions may be serialized. To see which campaign
classes can be serialized see [Individual interventions](parameter-campaign-individual-interventions.md). If the intervention
has been distributed to the person, then it will be serialized.  For example,
if the person received a bednet before the file was serialized, then the
serialized person will still have that bednet with however much its
performance has decayed.  However, if the person is supposed to receive drugs
if they become clinical and the person has not been clinical yet, then you
need to include that drug logic in your new campaign.