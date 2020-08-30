# Bibliotecas do Python necessarios para criar o Socket
import sys, struct, socket, json

def send_to_server(message, addr, port):
        # Resposta padrao
        answer = "NulL"

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
            	print 'Iniciando conexao!\nDestino: %s\nPorta: %d' % (answer["addr"], answer["port"])
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((answer["addr"], answer["port"]))
                print 'Para sair use CTRL+X\n'
                msg = raw_input()
                while msg <> '\x18':
            		sock.send (msg)
            		msg = raw_input()
                tcp.close()

# Programa Principal
if __name__ == '__main__':
    # Verifica os argumentos do programa
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        message = 'Backup Server?'
    # IP e porta padrao que sera utilizado
    except IndexError:
        addr = '225.0.0.1'
        port = 1905
        message = 'Backup Server?'
    # Execucao principal
    finally:
        print 'Enviando mensagem: %s\nDestino: %s\nPorta: %d' % (message, addr, port)
        send_to_server(message, addr, port)



