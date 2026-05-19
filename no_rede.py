import socket
import threading
import time
import sys

# SUBSTITUA OS IPS ABAIXO PELOS IPS REAIS DO HAMACHI
TABELA_NOS = {
    1: {"IP": "25.XX.XX.XX", "PORTA": 9871, "BATERIA": 95, "VIZINHOS": [2]},    
    2: {"IP": "25.YY.YY.YY", "PORTA": 9872, "BATERIA": 80, "VIZINHOS": [1, 3]}, 
    3: {"IP": "25.YY.YY.YY", "PORTA": 9873, "BATERIA": 85, "VIZINHOS": [2]},    
}

class NodoRede:
    def __init__(self, my_id):
        self.my_id = my_id
        self.ip = TABELA_NOS[my_id]["IP"]
        self.porta = TABELA_NOS[my_id]["PORTA"]
        self.bateria = TABELA_NOS[my_id]["BATERIA"]
        
        self.lider_id = None
        self.ultimo_heartbeat = time.time()
        self.em_eleicao = False
        self.votos_recebidos = []
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.porta)) 
        
        print(f"Nó {self.my_id} online! Bateria: {self.bateria}% | Porta: {self.porta}")
        print(f"Vizinhos de alcance de rádio: {TABELA_NOS[self.my_id]['VIZINHOS']}\n")
        
        threading.Thread(target=self.ouvir_rede, daemon=True).start()
        threading.Thread(target=self.monitorar_lider, daemon=True).start()

    def enviar_mensagem(self, msg, dest_id):
        
        if dest_id in TABELA_NOS:
            dest_ip = TABELA_NOS[dest_id]["IP"]
            dest_porta = TABELA_NOS[dest_id]["PORTA"]
            try:
                self.sock.sendto(msg.encode('utf-8'), (dest_ip, dest_porta))
            except Exception:
                pass 

    def enviar_para_vizinhos(self, msg):
        
        vizinhos = TABELA_NOS[self.my_id]["VIZINHOS"]
        for dest_id in vizinhos:
            self.enviar_mensagem(msg, dest_id)

    def ouvir_rede(self):
        
        while True:
            try:
                dados, addr = self.sock.recvfrom(1024)
                msg = dados.decode('utf-8')
                partes = msg.split("|")
                tipo_msg = partes[0]

                if tipo_msg == "HEARTBEAT":
                    id_lider = int(partes[1])
                    
                    
                    if self.lider_id == id_lider or self.lider_id is None:
                        if self.lider_id is None:
                            print(f"Líder {id_lider} detectado via propagação de vizinhos.")
                        
                        if time.time() - self.ultimo_heartbeat > 1.0:
                            self.lider_id = id_lider
                            self.ultimo_heartbeat = time.time()
                            
                            self.enviar_para_vizinhos(f"HEARTBEAT|{id_lider}")

                elif tipo_msg == "ELEICAO":
                    id_solicitante = int(partes[1])
                    print(f"Solicitação de eleição recebida do vizinho Nó {id_solicitante}.")
                    
                    self.enviar_mensagem(f"VOTO|{self.my_id}|{self.bateria}", id_solicitante)

                elif tipo_msg == "VOTO":
                    id_voto = int(partes[1])
                    bat_voto = int(partes[2])
                    if self.em_eleicao:
                        self.votos_recebidos.append((id_voto, bat_voto))

                elif tipo_msg == "NOVO_LIDER":
                    id_novo_lider = int(partes[1])
                    if self.lider_id != id_novo_lider:
                        self.lider_id = id_novo_lider
                        self.em_eleicao = False
                        self.ultimo_heartbeat = time.time()
                        print(f"NOVO LÍDER DA REDE DECLARADO: Nó {id_novo_lider}")
                        
                        self.enviar_para_vizinhos(f"NOVO_LIDER|{id_novo_lider}")

            except Exception as e:
                print(f"Erro no recebimento de dados: {e}")

    def monitorar_lider(self):
        
        while True:
            time.sleep(2)
            
            
            if self.lider_id == self.my_id:
                self.enviar_para_vizinhos(f"HEARTBEAT|{self.my_id}")
                
                self.bateria = max(0, self.bateria - 1)
                
            
            elif not self.em_eleicao:
                
                if (time.time() - self.ultimo_heartbeat > 6) or (self.lider_id is None):
                    print(f"\n[TIMEOUT] Líder antigo (Nó {self.lider_id}) falhou ou está fora de alcance!")
                    self.iniciar_eleicao()

    def iniciar_eleicao(self):
        
        print("Iniciando processo de eleição local com vizinhos alcançáveis...")
        self.em_eleicao = True
        self.votos_recebidos = []
        
        
        self.enviar_para_vizinhos(f"ELEICAO|{self.my_id}")

        
        time.sleep(2)
        
        maior_bateria = self.bateria
        vencedor_id = self.my_id
        
        
        for id_voto, bat_voto in self.votos_recebidos:
            if bat_voto > maior_bateria:
                maior_bateria = bat_voto
                vencedor_id = id_voto
            elif bat_voto == maior_bateria and id_voto > vencedor_id:
                vencedor_id = id_voto 
                
        print(f"Apuração local finalizada. Vencedor por critérios de energia: Nó {vencedor_id}")
        
        
        self.lider_id = vencedor_id
        self.enviar_para_vizinhos(f"NOVO_LIDER|{vencedor_id}")
        self.em_eleicao = False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso correto: python no_rede.py [ID_DO_NO]")
        sys.exit(1)
        
    id_escolhido = int(sys.argv[1])
    if id_escolhido not in TABELA_NOS:
        print("Erro: ID fornecido não existe na TABELA_NOS configurada.")
        sys.exit(1)
        
    nodo = NodoRede(id_escolhido)
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[DESCONECTADO] Desligando o Nó {id_escolhido} da infraestrutura sem fio.")