# Bibliotecas do Python necessarios para criar o Socket
import sys, struct, socket, json, thread
 
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
            info = '{"addr": "127.0.0.1", "port": "%d"}' % (port_tcp)
            answer = json.dumps(info)
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
    print '\nConectado ao cliente: %s' % (cliente)

    # Executa o loop de troca de mensagens, ate finalizar o Backup
    while True:
        msg = con.recv(1024)
        if not msg: break
        print cliente, msg

    print '\Conexao com o cliente %s encerrada!' % (cliente)
    con.close()
    thread.exit()
 
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





