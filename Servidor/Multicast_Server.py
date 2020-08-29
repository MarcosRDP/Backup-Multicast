# Bibliotecas do Python necessarios para criar o Socket
import sys, struct, socket, json
 
# Funcao que inicia o Servidor
def mcast_server(addr, port):
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
            print '\nEsperando por requisicoes!\n'
            data, addr_dest = fd.recvfrom(1024)
            answer = analise_pedido(addr_dest, addr, port, data)
            if(answer == 'null'):
            	print 'Requisicao: %s\nOrigem: %s\nNenhuma Resposta' % (data, addr_dest)
            else:
                print 'Requisicao: %s\nOrigem: %s\nResposta: %s' % (data, addr_dest, answer)
            	fd.sendto(answer, addr_dest)
    except KeyboardInterrupt:
        print 'done'
        sys.exit(0)

# Verifica o pedido recebido
def analise_pedido(addr_dest, addr, port, data):
        # Resposta padrao que indica que nao houve
        answer = 'null'
        # Verifica se a mensagem e para esse servidor
	if(data == 'Backup Server?'):
            info = '{"addr": "%s", "port": "%d"}' % (addr, port)
            answer = json.dumps(info)
        return answer
 
# Programa Principal
if __name__ == '__main__':
    # Verifica os argumentos do programa
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
    # IP e porta padrao que sera utilizado
    except IndexError:
        addr = '225.0.0.1'
        port = 1905
    # Execucao principal
    finally:
        print 'Executando o Servidor:\nIP: %s\nPorta:%d' % (addr, port)
        mcast_server(addr, port)
