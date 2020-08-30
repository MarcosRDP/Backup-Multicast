# Bibliotecas do Python necessarios para criar o Socket
import sys, struct, socket, json, os, shelve, shutil

#Recupera o nome dos arquivos e a ultima modificacao no cliente
def getFolderInfo(clientFolder):
    info = {}
    for folderName, subfolders, filenames in os.walk(clientFolder):
            for filename in filenames:
                lastModified = os.path.getmtime('%s/%s' % (folderName, filename))
                file = {filename:lastModified}
                info.update(file)
    return info

def send_to_server(message, addr, port, Folder_path):
        # Resposta padrao
        answer = "Null"

        multicast_group = (addr, port)

	# Inicia o Socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Adiciona um timeout para o Socket
	sock.settimeout(0.2)

	# Configura o Socket
	ttl = struct.pack('b', 1)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	try:
	    # Envia a mensagem para o grupo Multicast
            sent = sock.sendto(message, multicast_group)

    	    # Loop que aguarda resposta do Servidor
    	    while True:
            	print '\nAguardando resposta!'
            
            	try:
                        # Recebe mensagem do servidor
            		data, server_addr = sock.recvfrom(1024)
                # Verifica o Timeout programado
            	except socket.timeout:
                	print 'Tempo de resposta excedido!'
                	break
		# Apresenta os dados recebidos para o usuario
        	else:
            		print '\nResposta recebida: "%s"\nOrigem: %s' % (data, server_addr)
                        # Divide a resposta JSON recebida
                        answer = json.loads(data)
                        break
        # Finaliza o Socket
	finally:
    	    print '\nEncerando Socket de comunicacao Multicast!'
            sock.close()
            # Caso tenha recebido uma resposta, inicia a conexao TCP para o Backup
            if (answer != "Null"):
                # Verifica as informacoes sobre as pastas de backup
                info = json.dumps(getFolderInfo(Folder_path))
                # Avisa ao usuario que vai iniciar a conexao TCP
            	print 'Iniciando conexao!\nDestino: %s\nPorta: %d' % (answer["addr"], answer["port"])

                # Inicia a conexao TCP, com o endereco e porta passado pelo servidor Multicast
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((answer["addr"], answer["port"]))

                # Envia para o servidor a pasta que fara o Backup
                sock.send(info)

                msg = sock.recv(1024)
                listaArquivos = json.loads(msg)

		sock.send('Primeiro : 344')
           
                first = 1

                # inicia um loop com os arquivos
                for arquivo in listaArquivos:
                        if(first == 0):
				sock.send('Novo : 345')
			first = 0
			decide = ''
                	arq = open('%s/%s' % (Folder_path, arquivo), 'r')
                        while(decide != 'pronto'):
                                msg = sock.recv(1024)
                        	if(msg == 'Nome? : 346'):
                                	sock.send(arquivo)

                                if(msg == 'Continua : 347'):
                                	for i in arq.readlines():
                        			sock.send(i)
						msg = sock.recv(1024)
						if(msg != 'Continua : 347'):
							print 'Erro: %s\n' % (msg)
					decide = 'pronto'
                        arq.close()
		sock.send('Encerrou : 348')

                # Encerra a conexao TCP
                tcp.close()

# Programa Principal
if __name__ == '__main__':
    # Verifica os argumentos do programa
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        Folder_path = sys.argv[3]
    # IP e porta padrao que sera utilizado
    except IndexError:
        addr = '225.0.0.1'
        port = 1905
        Folder_path = './Teste'
    # Execucao principal
    finally:
        message = 'Backup Server?'
        print 'Enviando mensagem: %s\nDestino: %s\nPorta: %d' % (message, addr, port)
        send_to_server(message, addr, port, Folder_path)






