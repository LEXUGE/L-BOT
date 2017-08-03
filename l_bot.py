#!/usr/bin/python3

import telepot
import sys
import time
import types
import ast,math
import threading,os,signal

safe_dict = {
	"sin":math.sin,
	"cos":math.cos,
	"tan":math.tan,
	"pow":pow,
	"abs":math.fabs,
	"gcd":math.gcd,
	"sqrt":math.sqrt,
	"hypot":math.hypot,
	"log":math.log,
	"log2":math.log2,
	"pi":math.pi,
	"e":math.e
}

#class watch start
class Watcher:
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            print("[EXIT] Control-C")
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass

#class watch end

def safe_eval(source):
	tree = ast.parse(source, mode='eval')
	class Transformer(ast.NodeTransformer):
	    ALLOWED_NAMES = set(['+', '-','*','/','sin', 'cos','tan','pow','abs','gcd','sqrt','hypot','log','log2','pi','e','None', 'False', 'True'])
	    ALLOWED_NODE_TYPES = set([
			'Expression',
			'Tuple',
			'Call',
			'Name',
			'Load',
			'Str',

			'Num',
			'List',
			'Dict',
			'BinOp',
			'UnaryOp',
			'USub',
			'Add',
			'Sub',
			'Mult',
			'Div',
			'Mod'
	    ])

	    def visit_Name(self, node):
	        if not node.id in self.ALLOWED_NAMES:
	            raise RuntimeError("Name access to %s is not allowed" % node.id)
	        # traverse to child nodes
	        return self.generic_visit(node)

	    def generic_visit(self, node):
	        nodetype = type(node).__name__
	        if nodetype not in self.ALLOWED_NODE_TYPES:
	            raise RuntimeError("Invalid expression: %s not allowed" % nodetype)

	        return ast.NodeTransformer.generic_visit(self, node)


	transformer = Transformer()
	transformer.visit(tree)
	clause = compile(tree, '<AST>', 'eval')
	print(clause)
	result = eval(clause, dict(safe_dict))
	return result


def AUTH_BOT():
	global TOKEN
	global bot
	global bot_name
	TOKEN = sys.argv[1]
	bot = telepot.Bot(TOKEN)
	bot_name = '@'+bot.getMe()['username']

def INIT_MESSAGE():
	global count
	global offset
	global response
	count = 0
	offset = 0
	response = {}
	try:
		response_1 = bot.getUpdates()
	except:
		pass
	if len(response_1)-1>=0:
		response = response_1[len(response_1)-1]
		offset = response['update_id']+1

def MESSAGE_LOOP():
	global count
	global response
	global chat_message
	global chat_id
	global update_id
	global offset
	while (1):
		offset_old=offset
		count = count+1
		response = {}
		chat_message = 'No_Message'
		chat_id = 0
		update_id = 0
		try:
			response_1 = bot.getUpdates(offset=offset)
		except:
			pass
		if len(response_1)-1>=0:
			response = response_1[len(response_1)-1]
			#print(response)
			try:
				chat_message = response['message']['text']
			except:
				pass
			try:
				update_id = response['update_id']
			except:
				pass
			try:
				chat_id = response['message']['chat']['id']
			except:
				pass
			try:
				if '@' in chat_message:
					chat_message = chat_message.replace(bot_name, '')
			except:
				pass

			offset = update_id+1
		if offset!=offset_old:
			try:
				print("message: "+chat_message)
			except:
				pass
			try:
				print("offset: "+str(offset))
			except:
				pass
			try:
				print("chat_id: "+str(chat_id))
			except:
				pass
			print("",end="\n")
			threading.Thread(target=MESSSAGE_PROCCESS,args=(chat_id,chat_message),).start()
		time.sleep(0.5)

def MESSSAGE_PROCCESS(id_,message):
	if message.lower() == "/hello":
		bot.sendMessage(id_, 'Hey!')
	if message.lower() == "/help":
		bot.sendMessage(id_, "Hello!I'm LEXUGE's Telegram Bot.\nBLOG|LEXUGE:https://lexuge.github.io\n/hello:  greet to me\n/help:  send your this message\n/calc [expression]:  calculate the expression")
	if "/calc " in message.lower():
		try:
			bot.sendMessage(id_, safe_eval(chat_message[6:]))
		except:
			bot.sendMessage(id_, "Sorry!I can't calculate this.")
			pass


# Main Function
AUTH_BOT()
INIT_MESSAGE()

print("---Info---")
print(bot_name)
print(offset)
print("---End Info---")

Watcher()
MESSAGE_LOOP()
