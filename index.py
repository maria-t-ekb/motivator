from random import choice

import requests

from motivator.config import *


def handler(event, context):
    """
    Основная функция, в которой обрабатывается запрос пользователя,
    и которая определяет по какой ветке сценария необходимо дальше идтию
    """
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
    """
    Функция с пишет ответ на сообщение пользователя,
    если не помогла основная лоогика навыка.
    Если сообщение до 100 токенов запрашиваем ответ у нейросети,
    иначе просим уточнить запрос.
    """
    tokens = event['request'].get('nlu', {}).get('tokens')
    if len(tokens) < 100:
        text = event['request']['original_utterance']
        answer = ai_answer(text)
    else:
        answer = 'Извини, но я тебя не совсем поняла. Для продолжения диалога со мной расскажи как у тебя дела?'
    return make_response(answer, state=state)


def ai_answer(text):
    """Функция отправляет запрос нейросети и возвращает её ответ"""
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
    return answer


def button_answer(request, state=None):
    """Функция пишет ответ на кнопку, которую нажал пользователь"""
    text = answer_button[request]['text']
    image = answer_button[request]['image']
    return make_response(text, state=state, image=image)


def button(title, hide=False):
    """Функция создаёт описание кнопки"""
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
    """Функция формирует ответ пользователю"""
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


event_1 = {
  "meta": {
    "locale": "ru-RU",
    "timezone": "UTC",
    "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
    "interfaces": {
      "screen": {},
      "payments": {},
      "account_linking": {}
    }
  },
  "session": {
    "message_id": 0,
    "session_id": "7beafe2f-c7d0-4a8d-8439-09e5c8dbd34e",
    "skill_id": "afa15a5c-65e7-447b-8935-a5d460c8e248",
    "user": {
      "user_id": "8C83541E5498BBD96D0027727FF1DDC456DC3BB31DEA70F1E283D0EAEFC8B15D"
    },
    "application": {
      "application_id": "443172C73D84F601BFAC49E3426A1C9B063C977173B7BC2C4C3765CF1C34C779"
    },
    "new": True,
    "user_id": "443172C73D84F601BFAC49E3426A1C9B063C977173B7BC2C4C3765CF1C34C779"
  },
  "request": {
    "command": "",
    "original_utterance": "",
    "nlu": {
      "tokens": [],
      "entities": [],
      "intents": {}
    },
    "markup": {
      "dangerous_context": False
    },
    "type": "SimpleUtterance"
  },
  "state": {
    "session": {},
    "user": {},
    "application": {}
  },
  "version": "1.0"
}
event_2 = {
  "meta": {
    "locale": "ru-RU",
    "timezone": "UTC",
    "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
    "interfaces": {
      "screen": {},
      "payments": {},
      "account_linking": {}
    }
  },
  "session": {
    "message_id": 2,
    "session_id": "07f93cfc-308d-4ffe-8b09-da3684c84dbe",
    "skill_id": "afa15a5c-65e7-447b-8935-a5d460c8e248",
    "user": {
      "user_id": "8C83541E5498BBD96D0027727FF1DDC456DC3BB31DEA70F1E283D0EAEFC8B15D"
    },
    "application": {
      "application_id": "443172C73D84F601BFAC49E3426A1C9B063C977173B7BC2C4C3765CF1C34C779"
    },
    "new": False,
    "user_id": "443172C73D84F601BFAC49E3426A1C9B063C977173B7BC2C4C3765CF1C34C779"
  },
  "request": {
    "command": "мне грустно",
    "original_utterance": "мне грустно",
    "nlu": {
      "tokens": [
        "мне",
        "грустно"
      ],
      "entities": [],
      "intents": {
        "sad_situation": {
          "slots": {}
        }
      }
    },
    "markup": {
      "dangerous_context": False
    },
    "type": "SimpleUtterance"
  },
  "state": {
    "session": {},
    "user": {},
    "application": {}
  },
  "version": "1.0"
}
context = None
print(handler(event_1, context))
print(handler(event_2, context))
