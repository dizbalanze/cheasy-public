import my_config
import openai
import threading
import time

openai.api_key = my_config.openai_key

def request_with_timeout(messages, temperature, model, result_container, event):
    try:
        completion = openai.chat.completions.create(model=model, messages=messages, temperature=temperature)
        if not event.is_set():
            result_container['result'] = completion.choices[0].message.content
    except Exception as e:
        if not event.is_set():
            result_container['error'] = e


def create_completion(messages, temperature=0.2, model='gpt-3.5-turbo-1106', timeout=60):
    print("\033[32mRequest received\033[0m")
    print(messages)
    retry_int = 0
    while True:
        result_container = {}
        event = threading.Event()
        thread = threading.Thread(target=request_with_timeout, args=(messages, temperature, model, result_container, event))
        thread.start()
        thread.join(timeout)
        event.set()

        if 'result' in result_container:
            return result_container['result']
        elif 'error' in result_container:
            raise result_container['error']

        print(f'\033[31mTimeout, retrying... ({retry_int})\033[0m')
        time.sleep(5)

pp =  [{"role": "user", "content": 'Кто такой Тоби Магуаер?'}]
