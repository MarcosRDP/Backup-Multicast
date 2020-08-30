# Bibliotecas do Python necessarios para criar o Socket
import sys, struct, socket, json, thread, os, shelve, shutil
 
# Funcao que inicia o Servidor
def mcast_server(addr, port, port_tcp):
    # Inicia o Socket
    fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
    # Liga o Socket a porta definida
    fd.bind(('', port))
 
    # Se conecta ao grupo Multicast
    mreq = struct.pack('4sl', socket.inet_aton(addr), socket.INADDR_ANY)
    fd.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
 
    # Inicia o Loop que recebe informacoes
    try:
        while 1:
            data, addr_dest = fd.recvfrom(1024)
            answer = analise_pedido(data, port_tcp)
            # Printa na tela o tipo de resposta dado e responde o usuario
            if(answer == 'null'):
            	print 'Requisicao: %s\nOrigem: %s\nNenhuma Resposta' % (data, addr_dest)
            else:
                print 'Requisicao: %s\nOrigem: %s\nResposta: %s' % (data, addr_dest, answer)
            	fd.sendto(answer, addr_dest)
    except KeyboardInterrupt:
        print '\nServidor Multicast encerrado!'
        thread.exit()

# Verifica o pedido recebido
def analise_pedido(data, port_tcp):
        # Resposta padrao que indica que nao houve
        answer = 'null'
        # Verifica se a mensagem e para esse servidor
	if(data == 'Backup Server?'):
            answer = '{"addr": "127.0.0.1", "port": %d}' % (port_tcp)
        return answer

# Cria a conexao TCP
def tcp_server(port_tcp):
        # Inicia um Socket TCP e liga a porta ao Socket
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.bind(('', port_tcp))

        # Inicia o processo do TCP 
        fd.listen(1)

        try:
            while True:
                con, cliente = fd.accept()
                thread.start_new_thread(conect_TCP, tuple([con, cliente]))
        except KeyboardInterrupt:
            fd.close()
            print '\nServidor TCP encerrado!'
            sys.exit(1)

# TCP Conectado
def conect_TCP(con, cliente):
    print '\nConectado ao cliente: %s' % (str(cliente))

    # Executa o loop de troca de mensagens, ate finalizar o Backup
    while True:
        # Recebe a mensagem com as pastas para o Backup
        msg = con.recv(1024)
        if not msg: break
        clientFolderBlueprint = json.loads(msg)

        # Cria um Log com as operacoes de Backup feitas
        backupLog = shelve.open('./log/backupLog')

        # Cria lista com os armazenamentos
        requestTwo = backupActions(clientFolderBlueprint, backupLog)
        requestTwo = json.loads(requestTwo)
        requestToAdd = requestTwo["requestToAdd"]
        requestToSend = json.dumps(requestToAdd)
        requestToDelete = requestTwo["requestToDelete"]

        # Envia uma mensagem para o cliente com os arquivos necessarios
        con.send(requestToSend)

	# Inicia um loop, ate receber todos os arquivos
        while True:
            # Recebe os dados
            dados = con.recv(1024)

            # Verifica se e o codigo que indica o primeiro arquivo
            if(dados == 'Primeiro : 344'):
                # Vai requirir o nome do arquivo
            	con.send('Nome? : 346')
                # Recebe o nome do arquivo e o abre
                dados = con.recv(1024)
                arq = open('./Backup/%s' % (dados), 'w')
                # Indica ao cliente que pode continuar
                con.send('Continua : 347')

            # Verifica se e o codigo que indica um novo arquivo
            elif(dados == 'Novo : 345'):
                # Fecha o arquivo
                arq.close()
                # Vai requirir o nome do arquivo
            	con.send('Nome? : 346')
                # Recebe o nome do arquivo e o abre
                dados = con.recv(1024)
                arq = open('./Backup/%s' % (dados), 'w')
                # Indica ao cliente que pode continuar
                con.send('Continua : 347')

            elif(dados == 'Encerrou : 348'):
                # Fecha o arquivo
                arq.close()
                # Encerra a comunicacao com o
                print '\nConexao com o cliente %s encerrada!' % (str(cliente))
                con.close()
                thread.exit()

            else:
                arq.write(dados)
                # Indica ao cliente que pode continuar
                con.send('Continua : 347')
    

def backupActions(clientFolderBlueprint, backupLog):
    #Variaveis
    requestToAdd = []
    requestToDelete = []

    #Abre arquivos no backup
    #Le nome dos arquivos armazenados no backup
    backupLogFiles = list(backupLog.keys())        
    for filename in backupLogFiles:
        #Checa se arquivo existente no backup tambem existe no cliente
        if(clientFolderBlueprint.get(filename)):
            #Checa se o arquivo no cliente foi modificado
            if(clientFolderBlueprint[filename] != backupLog[filename]):
                requestToDelete.append(filename)
                requestToAdd.append(filename)
                backupLog[filename] = clientFolderBlueprint[filename]
        else:
            requestToDelete.append(filename)
            del backupLog[filename]
    #Checa quais arquivos devem ser adicionadors ao backup
    toBeAdded = [key for key in clientFolderBlueprint.keys() if key not in backupLogFiles]
    requestToAdd.extend(list(toBeAdded))
    x = json.dumps(requestToAdd)
    y = json.dumps(requestToDelete)
    answer = '{ "requestToAdd" : %s, "requestToDelete" : %s }' % (x, y)
    return answer
    

#Adiciona os arquivos a pasta de backup  simulacao da acao do servidor ao recever os arquivos atualizados do cliente
def sendToBackupFolder():
    for filesToAdd in requestToAdd:
        shutil.copy2(os.path.join(clientFolder,filesToAdd),os.path.join(backupFolder,filesToAdd))
        backupLog[filesToAdd] = clientFolderBlueprint[filesToAdd]

#Remove arquivos da pasta backup e atualiza historico 
def manageBackupHistory():
    for filesToDelele in requestToDelete:
        os.unlink(os.path.join(backupFolder,filesToDelele))
        del backupLog[filesToDelele]
 
# Programa Principal
if __name__ == '__main__':
    # Verifica os argumentos do programa
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        port_tcp = int(sys.argv[3])
    # IP e porta padrao que sera utilizado
    except IndexError:
        addr = '225.0.0.1'
        port = 1905
        port_tcp = 5000
    # Execucao principal
    finally:
        print 'Executando o Servidor:\nIP: %s\nPorta: %d\nPorta do TCP: %d' % (addr, port, port_tcp)
        thread.start_new_thread(tcp_server, tuple([port_tcp]))
        mcast_server(addr, port, port_tcp)

####
#
#requestToDelete = []
#requestToAdd = []

#folderName = 'backup'
#backupFolder = os.path.join(os.getcwd(),folderName)





