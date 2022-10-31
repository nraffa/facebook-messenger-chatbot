import gspread
import pandas as pd
import difflib
import base64
import os
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from string import ascii_lowercase
import requests
from datetime import datetime



#tokens for chat_support app
#--------------------------------------------------------
FB_API_URL = 'https://graph.facebook.com/v13.0/me/messages'
VERIFY_TOKEN = os.environ['VERIFY_TOKEN'] 
PAGE_ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN'] 
APP_ID = os.environ['APP_ID']
#--------------------------------------------------------

PAGE_ID = os.environ['PAGE_ID']

#tokens for inbox app
#--------------------------------------------------------
PAGE_ACCESS_TOKEN_INBOX = os.environ['PAGE_ACCESS_TOKEN_INBOX']
FB_INBOX_APP_ID = os.environ['FB_INBOX_APP_ID']

# Config for service account (google sheets access)
#----------------------------------------------------------------------------------
gc = gspread.service_account(filename='google-credentials.json') #for ngrok testing take the filename parameter out
sh = gc.open("bot_database")
df = pd.DataFrame(sh.worksheet('responses').get_all_records())

# Config for email account (gmail api access)
#----------------------------------------------------------------------------------
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

creds = None
if os.path.exists('token.json'):
	creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
	else:
		flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
		creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open('token.json', 'w') as token:
		token.write(creds.to_json())


service = build('gmail', 'v1', credentials=creds)


def create_message(sender, to, subject, message_text):
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
	try:
		message = (service.users().messages().send(userId=user_id, body=message)
				   .execute())
		print('Message Id: %s' % message['id'])
		return message
	except Exception as error:
		print(error)


# Emojis
#----------------------------------------------------------------------------------
nl = '\n'
email = u'\U0001F4E7'
heart_face = u'\U0001F60D'
clock = u'\U0001F55B'
pin = u'\U0001F4CD'
telephone = u'\U0000260E'
money = u'\U0001F4B5'
book = u'\U0001F4D6'
guinio = u'\U0001F609'
eyes = u'\U0001F440'
waving_hand = u'\U0001F44B'
person_raising_hand = u'\U0001F64B'
robot = u'\U0001F916'

#list for persistent menu
persistent_menu = ['sitio web', 'contactar a un asesor', 'menu principal']
#intent for greeting
question_intent = ['hola','buenas','menu principal','info','precio','mafalda','empezar']
#intent for services (question)
services = [code.lower() for code in df['code'].unique()]
#intent for goodbye
goodbye = ['mas tarde']
#intent for unstateful questions
unstate = []
all = services + question_intent 

def GetMostSimilarWord(message,intent_list):
	"""Get the most similar word out from the intent list"""
	message = message.lower()   
	possible_words = difflib.get_close_matches(message, intent_list)

	if len(possible_words) > 0:
		return possible_words[0]
	else:
		return message


def GetIntentOfMessage(message):
	#get the intent from the message
	msg = message.lower()
	most_similar_word = GetMostSimilarWord(msg,all)

	if most_similar_word in question_intent:
		return ('question',1)
	if most_similar_word == df.loc[(df.service=='Contactar a un asesor'), 'code'].item():
		return ('human_tag',2)
	if most_similar_word in services:
		return ('info',3) 
	if most_similar_word == 'mafalda':
		return ('robot_tag',1)
	if most_similar_word in goodbye:
		return ('goodbye',1)
	return ('none',1)

def Greeting(message,recipient_id):
	"""If someone says 'hola' or 'buenas' to us, use this function to
	respond with a greeting and initial menu options"""
	
	most_similar_word = GetMostSimilarWord(message,question_intent)

	#payload variables
	nl = '\n'
	if most_similar_word in question_intent:
		initial_response = f"{robot}Hola, gracias por contactarte! Soy Mafalda, la asistente virtual de Cle y estoy aqui para guiarte.{nl}¿En que servicio tenes interes?{nl}"
		messaging_type = "RESPONSE"
		quick_replies = []

		for i in range(len(df)):
			#append the service name to the initial response text
			initial_response += f"{nl}{df['code'].iloc[i].upper()}. {df['service'][i]}"
			quick_replies.append({
							"content_type": "text",
							"title": df['code'].iloc[i].upper(),
							"payload": "<POSTBACK_PAYLOAD>"
						}
						)
	   
		initial_payload = {
				"recipient": {
					"id": recipient_id
				},
				"messaging_type": messaging_type,
				"message": {
					"text": initial_response,
					"quick_replies": quick_replies
					}
			}

		return initial_payload

def Goodbye(sender):
	"""If someone says 'mas tarde' to us, use this function to
	respond with a goodbye message"""
	
	bye_text = f"{waving_hand} ¡Gracias por contactarte con Clé Coaching!"

	bye_payload = {
			"recipient": {
				"id": sender
			},
			"message": {
				"text": bye_text
				}
		}

	return bye_payload


def GetInfoOfService(df,message,sender):
	"""This function will return the info of the service selected 
		by looking for the info in the df coming from the google spreadsheet"""

	payload_1,payload_2,payload_3 = '','',''
	messaging_type = "RESPONSE"

	message = message.lower()
	
	df_info = df[df['code'] == message]
	df_info = df.reset_index(drop=True)

	most_similar_word = GetMostSimilarWord(message,services)	

	if most_similar_word == df.loc[(df.service=='Agendar una cita'), 'code'].item():
		query_response = f'Genial! Le dejo a continuacion un link donde podra agendar un encuentro con nuestro Coach en función de la disponibilidad:{nl}{nl}https://calendly.com/clecoaching/1hour.{nl} Tener en cuenta que el encuentro solo tendra lugar si ya se ha realizado una consulta previa.{guinio}Tip: escribi "menu principal" para volver a las primeras opciones.'
		
		query_payload = {
			"recipient": {
				"id": sender
			},
			"message": {
				"text": query_response
				}
		}
		return query_payload
	
	# if most_similar_word == df.loc[(df.service=='Contactar a un asesor'), 'code'].item():

		
	#     message = create_message('me', 'nraffapirra@gmail.com', 'hello', 'se mando satisfactoriamente el mail! \nAlfred!!')
	#     print(send_message(service=service, user_id='me', message=message))

	#     query_payload = {
	#         "recipient": {
	#             "id": sender
	#         },
	#         "message": {
	#             "text": f"Genial, te transfiero con nuestra asesora principal. Se contactara con vos lo antes posible!{nl}{nl}{email}Recordá que también podés escribirnos a info@clecoaching.com."
	#             }
	#     }

	#     """https://graph.facebook.com/LATEST-API-VERSION/PAGE-ID/take_thread_control
	# ?recipient={id:PSID}
	# &metadata=Information about the conversation
	# &access_token=PAGE_ACCESS_TOKEN"""




	#     return query_payload


	if most_similar_word in services and most_similar_word != df.loc[(df.service=='Contactar a un asesor'), 'code'].item():

		index = services.index(most_similar_word)

		payload_1 = {
		"recipient": {
			"id": sender
		},
		"message": {
			"text": f"""Nos alegra saber que tenes interes en nuestro servicio de {df['service'].iloc[index]}. Te dejo a continuacion la informacion necesaria:{nl}
			{nl}{heart_face}{df_info['description'].iloc[index]}
			{nl}{clock}{df_info['schedule'].iloc[index]}
			{nl}{pin}{df_info['location'].iloc[index]}
			{nl}{telephone}{df_info['contact_info'].iloc[index]}
			{nl}{money}{df_info['price'].iloc[index]}
			{nl}{book}Te mando un pdf con toda la informacion de este servicio para que tengas todos los detalles:"""
			}
		}

		payload_2 = {
		"recipient": {
			"id": sender
		},
		"message": {
			"attachment": {
				"type":"file",
				"payload":{
					"url": df_info['pdf_link'].iloc[index],
					"is_reusable": "True"
					}
				}
			}
		}
		
		
		if df_info['schedule_when_inquiry'].iloc[index] == 'si':


			payload_3 = {
				"recipient": {
					"id": sender
				},
				"messaging_type": messaging_type,
				"message": {
					"attachment": {
						"type": "template",
						"payload": {
							"template_type": "generic",
							"elements": [
								{
									"title": f'{telephone}¿Queres agendar una primera cita?',
									"subtitle": f'{eyes}La misma se descontara del pack.',
									"buttons": [
										{
											"type": "web_url",
											"url": "https://calendly.com/clecoaching/1hour?month=2022-07",
											"title": 'Agendar Cita'
										},{
											"type": "postback",
											"title": "Más Tarde",
											"payload": "mas tarde"
										}
									]
								}
							]
						}
					}
				}
			}

		else: 
			payload_3 = {
				"recipient": {
					"id": sender
				},
				"message": {
					"text": f"""¿Tenes interes en algun otro servicio?{nl}{guinio}Tip: escribi 'menu principal' para volver a las primeras opciones.""",
				}
			}

		return (payload_1,payload_2,payload_3)
	
	


def GenericResponse(sender):
	
	generic_payload = {
		"recipient": {
			"id": sender
		},
		"message": {
			"text": 'Disculpa - No se bien como ayudarte con eso'
			}
	}

	return generic_payload

def HumanTagResponse(message,sender):

	message = message.lower()

	most_similar_word = GetMostSimilarWord(message,df.loc[(df.service=='Contactar a un asesor'), 'code'].item())	

	if most_similar_word == df.loc[(df.service=='Contactar a un asesor'), 'code'].item():

		#get user info
		user_info_url = f"https://graph.facebook.com/{sender}?fields=first_name,last_name,profile_pic&access_token={PAGE_ACCESS_TOKEN}"
		user_first_name = requests.get(user_info_url).json()['first_name']
		user_last_name = requests.get(user_info_url).json()['last_name']
		time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

		email_content = f"""Cle Coaching {nl}{nl}
								{nl}👋 Hola! Este email, de uso interno, es para notificarte que un usuario {user_first_name} {user_last_name} solicito contactar a un humano a las {time}.{nl}
								{nl}✨ Al recibir la solicitud por parte del usuario, le encomande a Mafalda que apague sus funcionalidades (para este usuario en particular) para que puedas comunicarte sin problemas con el a traves del Meta Business Suite.{nl}
								{nl}⬇️ Una vez que hayas finalizado y estes 100% con seguridad de que el usuario esta satisfecho con la respuesta brindada por el colega humano, para que vuelva de mi siesta, debes hacer click en el tick de LISTO y ahi Mafalda retomara sus funciones.{nl}
								{nl}📬 Trata de comunicarte a la brevedad que si no le dire a Mafalda que vuelva a tomar control de conversacion!!.{nl}
								
								{nl}💃 Espero que hayas disfrutado de mis servicios.{nl}
								{nl}{robot}Alfred."""

		message = create_message('me', 'nraffapirra@gmail.com', f'FB Messenger - Respuesta Necesaria: {user_first_name} {user_last_name}' , email_content)
		print(send_message(service=service, user_id='me', message=message))

		payload_1 = {
			"recipient": {
				"id": sender
			},
			"message": {
				"text": f"{person_raising_hand} Te transfiero con nuestra asesora principal. Se contactara con vos lo antes posible!{nl}{nl}{email}Recordá que también podés escribirnos a info@clecoaching.com."
				}
		}

		payload_2 = {
			"recipient": {
				"id": sender
			},
			"message": {
				"text": f"{guinio}Tip: Si me llamas, escribiendo 'Mafalda', voy a volver para asistirte."
				}
		}


		return payload_1,payload_2

def HandoverProtocol(sender):
	#send post request to request thread control (the inbox app requests control of the thread)
	request_url = f'https://graph.facebook.com/v13.0/{PAGE_ID}/request_thread_control?recipient={{"id":"{sender}"}}&access_token={PAGE_ACCESS_TOKEN_INBOX}'
	print(requests.post(request_url))

	#send post request to pass thread control (the primary app passes control of the thread to the page inbox)
	pass_url = f'https://graph.facebook.com/v13.0/{PAGE_ID}/pass_thread_control?recipient={{"id":"{sender}"}}&target_app_id={FB_INBOX_APP_ID}&access_token={PAGE_ACCESS_TOKEN}'
	print(requests.post(pass_url))

def RobotTakeOver(sender):
	#take control 
	take_url = f'https://graph.facebook.com/v13.0/{PAGE_ID}/take_thread_control?recipient={{"id":"{sender}"}}&target_app_id={APP_ID}&access_token={PAGE_ACCESS_TOKEN}'
	print(requests.post(take_url))

def GetResponseBasedOnIntent(intent, message,sender):
	# Define the rules (keys-> intent // values ->  response)
	df = pd.DataFrame(sh.worksheet('responses').get_all_records())
	rules = {
		"question": Greeting(message,sender),
		"none": GenericResponse(sender),
		#"specify_service": ChoosedService(message,sender),
		"info": GetInfoOfService(df,message,sender),
		"human_tag": HumanTagResponse(message,sender),
		"goodbye": Goodbye(sender)
	}

	return rules[intent]

# MAIN FUNCTION

def GetBotResponse(message,sender):
	"""This is the main function of our Bot. It has payloads as an output"""

	message = message.lower()    

	#Get response base on the intent
	intent = GetIntentOfMessage(message)[0]
	#if the intent is info >> this will have a tuple as an output with multiple payloads (for the message and the pdf)
	final_payload = GetResponseBasedOnIntent(intent, message,sender)  

	return final_payload