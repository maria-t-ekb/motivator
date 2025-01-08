from random import choice
import requests
from config import *


def handler(event, context):
    '''Основная функция'''
    intents = event['request'].get('nlu', {}).get('intents')
    state = event.get('state', {}).get('session', {})
    payload = event.get('request').get('payload', {})
    
    situation = None
    for key in intents.keys():
        if key in intent_situations:
            situation = intent_situations[key]
            break
    
    if event['session']['new']:
        situation = intent_situations['welcome']

    if 'screen' in state and 'button' in state.get('screen').get('situation') and 'session_state' in payload:
        request = payload['session_state']
        return button_answer(request, state=state)
    elif situation:
        return make_response(choice(situation['text']), situation['image'], situation['buttons'], state=state)
    else:
        return fallback(event, state=state)


def fallback(event, state=None):   
    tokens = event['request'].get('nlu', {}).get('tokens')
    if len(tokens) > 100:
        text = 'Извини, но я тебя не совсем поняла. Для продолжения диалога со мной расскажи как у тебя дела?'
        return make_response(text, state=state)
    else:
        text = event['request']['original_utterance']
        prompt = {
            "modelUri": "gpt://b1gq8d63dakb7v0surrh/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "100"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты мотиватор"
                },
                {
                    "role": "user",
                    "text": text
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key AQVNxwy2N83Q7rzZuAA30kbN2-RYIoZECeGZVKc_"
        }

        response = requests.post(url, headers=headers, json=prompt)
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        return make_response(answer, state=state)


def button_answer(request, state=None):
    text = answer_button[request]['text']
    image = answer_button[request]['image']
    return make_response(text, state=state, image=image)


def button(title, hide=False):
    button = {
        'title': title,
        'payload': {
            'session_state': title,
            'type': 'ButtonPressed'
        },
        'hide': hide,
    }
    return button


def make_response(text, image=None, button_blanks=None, state=None):
    response = {
        'text': text,
        'tts': text,
        'end_session': False,
    }
    
    if button_blanks is not None:
        buttons = []
        for new_button in button_blanks:
            buttons.append(button(new_button['text'], new_button['hide']))
        response['buttons'] = buttons
        if 'screen' not in state:
            state['screen'] = {}
        state['screen']['situation'] = 'button'
    
    if image:
        card = {
            'image_id': image,
            'type': 'BigImage',
            'description': text
        }
        response['card'] = card
        
    all_response = {
        'response': response,
        'version': '1.0',
    }

    if state:
        all_response['session_state'] = state
    return all_response
