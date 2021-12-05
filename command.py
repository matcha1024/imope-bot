from tweet import doReply
command_list = ['hello']
def doCommand(command,id,data):
    message = 'そのコマンドは存在しないか、打ち間違えです。固定ツイートを参照して下さい。'
    if not command in command_list:
        doReply(message,id)
        return
    
    if command == 'hello':
        message = 'hello! ' + data['user']['name']
        doReply(message,id)
        return