# Mafalda: a Cle Coaching conversational assistant
(or chatbot in not fancy words)

In this repository, you will find the source code for the chatbot of Cle Coaching for **facebook messenger**. More information on Cle, can be found here: 

https://www.clecoaching.com/

Chatbot based on Facebook Messenger API. The chatbot was deployed in heroku. Features of Google Cloud Platform (GCP) were used as well (gmail, sheets APIs).

## Objective
Cle Coaching is a start up, which I can proudly say, builded by my mother. The idea was to relieve her of some work load and have this chatbot answer the most frequent questions (FAQs).
The logic behind was to get intent based on specific wording of the client messages. 

Some other nice features of the chatbot were:
- Get the latest information on the companies services provided, uploaded by Cle Coaching managers from google spreadsheets. :loudspeaker:
- Send email notifications when the customer requested to talk to a human :incoming_envelope:
- Used the Handover Protocol of Facebook's API so that there was a smooth transition between Chatbot's messages and Cle Coaching's employees. :robot: <--> :information_desk_person:


## Out of scope
- NLP implementation. As next improvements for the chatbot, NLP and smarter detection on intents is planned. 
- Statefullness: the chatbot doesn't recognize in which state of the conversation it is. Each message is a fresh start, which for a conversation flow can be problematic.

## Examples of the conversation

![Captura de pantalla 2022-10-29 172326](https://user-images.githubusercontent.com/50913652/198839983-c981fb27-a0e2-4ec3-bcbc-cbceb15b224f.jpg)

![Captura de pantalla 2022-10-29 172355](https://user-images.githubusercontent.com/50913652/198839988-2fe7d82f-73bb-4653-8c62-5f7eaf94f262.jpg)

![Captura de pantalla 2022-10-29 172417](https://user-images.githubusercontent.com/50913652/198839990-1358160e-7a9e-4714-9349-3ba3a17d68bd.jpg)

HANDOVER PROTOCOL

![Captura de pantalla 2022-10-29 172441](https://user-images.githubusercontent.com/50913652/198839993-31d005c0-9dd9-4bb7-8759-edcbf42cf4df.jpg)

EMAIL NOTIFICATION FOR CLE COACHING EMPLOYEE TO TAKE OVER OF CHAT

![image](https://user-images.githubusercontent.com/50913652/198839955-dacdd983-b552-4564-9c65-37664cc664b2.png)
