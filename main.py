import pprint
import random
import requests
import websocket
import json
import pickle

message = "I like pussy I like pasta I like pussy I like dogs"
ws_token = "xapp-1-A04T2R50WDD-4935429363122-a6dbe0662484dd1bbe9d02d0b677f418be8a8654efcb79250bbc3b4814c125d9"
ws_api_url = "https://slack.com/api/apps.connections.open"
message_api_url = "https://slack.com/api/chat.postMessage"
api_token = "xoxb-500173009233-4928817611110-1pxqFw7IRjsE0BTrYUuElQK8"

try:
    tree = eval(open("tree.txt", "r").read())
except:
    tree = dict()

def get_sentence(tree, k):
    if tree[k] == []:
        return k
    else:
        random_v = random.choice(tree[k])
        return k + get_sentence(tree,random_v)

def generate_sentence(tree, k):
    return " ".join(get_sentence(tree, k))

def generate_tree(message):
    words = message.split()
    triplets = []
    words_pairs = []
    tree = dict()
    for i in range(0, len(words), 3):
        triplets.append(tuple(words[i:i+3]))

    for i in range(0, len(triplets)):
        words_pairs.append(tuple(triplets[i:i+2]))

    for pair in words_pairs:
        first, *second = pair
        values = tree.get(first, [])
        tree.update({first: values + second or []})
    return tree

def merge_trees(tree1, tree2):
    for k in tree2:
        values = tree1.get(k, [])
        tree1.update({k: list(set(values + tree2.get(k, [])))})
    return tree1

ws_url = requests.post(ws_api_url, headers={"Authorization": "Bearer " + ws_token}).json()['url']

def on_error(ws, error):
    print("error")
    print(error)

def on_message(ws, message):
    global tree
    ws.send(message)

    message_json = json.loads(message.replace('<@U04TAQ1HZ38>', ''))
    message_event = message_json['payload']['event']
    message_channel = message_event['channel']
    message_text = message_event['text']
    bot_id = message_event.get('bot_id', None)

    match message_event['type']:
        case "message":
            if bot_id == None:
                print("its a message!")
                message_tree = generate_tree(message_text)
                tree = merge_trees(tree, message_tree)
                with open(r'tree.txt','w') as f:
                    f.write(str(tree))
        case "app_mention":
            print("its a mention!")
            sentence = generate_sentence(tree,random.choice(list(tree.keys())))
            message_payload = dict(channel=message_channel, text=sentence)
            message_post = requests.post(message_api_url, json=message_payload,  headers={"Authorization": "Bearer " + api_token}).json()


ws = websocket.WebSocketApp(ws_url,
                            on_message=on_message,
                            on_error=on_error)

ws.run_forever()
