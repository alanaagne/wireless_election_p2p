# 🔋 Energy-Aware Wireless Election P2P

Este projeto foi desenvolvido como parte do **Seminário de Sistemas Distribuídos**. O sistema implementa um algoritmo de eleição de líder customizado para **Ambientes Sem Fio (redes ad-hoc ou redes de sensores)** utilizando uma arquitetura puramente Peer-to-Peer (P2P).

## 🚀 Sobre o Projeto

Em ambientes sem fio reais, os nós possuem restrições severas de energia (bateria) e raio limitado de alcance de rádio. Algoritmos tradicionais (como o do Valentão ou em Anel) tornam-se inviáveis devido ao alto custo de mensagens globais. 

Este projeto resolve esse problema através de:
1. **Restrição de Topologia (Visibilidade por Vizinhos):** Os nós não conhecem a rede inteira; eles só podem se comunicar diretamente com os vizinhos contidos no seu raio de alcance.
2. **Eleição Baseada em Energia Remanescente:** O critério de escolha do coordenador (Leader/Cluster Head) baseia-se na maior porcentagem de bateria disponível, estendendo o tempo de vida útil da rede.
3. **Reeleição Dinâmica por Heartbeat:** O líder envia periodicamente um sinal de "estou vivo". Caso o processo do líder caia (falha física ou descarregamento), os vizinhos detectam a ausência por *timeout* e iniciam uma nova eleição de forma autônoma.

## 🛠️ Tecnologias e Conceitos Aplicados

* **Linguagem:** Python 3
* **Protocolo de Transporte:** UDP (User Datagram Protocol) - escolhido pela baixa latência e ausência de handshake permanente.
* **Concorrência:** Multi-threading (Threads separadas para escuta de rede e monitoramento de timeouts).
* **Comunicação Baseada em Inundação Local (Neighbor Flood).**
* **Tolerância a Falhas e Sistemas Autoreconfiguráveis.**

## ⚙️ Arquitetura da Rede Sem Fio

A rede é modelada através de uma tabela de adjacência IP/Porta onde definimos estritamente quem consegue "ouvir" quem. Exemplo de topologia simulada em linha:

* **Nó 1 (Máquina A):** Só alcança o Nó 2.
* **Nó 2 (Máquina B - Terminal 1):** Ponte central, alcança o Nó 1 e o Nó 3.
* **Nó 3 (Máquina B - Terminal 2):** Só alcança o Nó 2.

## 📦 Como Instalar e Rodar

### Pré-requisitos
* Python 3 instalado em todas as máquinas.
* Uma rede virtual ativa (como o LogMeIn Hamachi) caso o teste seja feito em computadores geograficamente distantes.
* O projeto utiliza apenas bibliotecas nativas do Python (Standard Library), logo, não é necessário instalar dependências externas via pip.

### Configuração
1. Abra o arquivo `no_rede.py`.
2. Altere os IPs da estrutura `TABELA_NOS` para os IPs reais das interfaces de rede/Hamachi que serão utilizadas.

### Execução

**Na Máquina Nó 1:**
```bash
python no_rede.py 1
```

**Na Máquina Nó 2 e Nó 3 (em terminais separados):**
```bash
# Terminal 1
python no_rede.py 2

# Terminal 2
python no_rede.py 3
```

* Ao encerrar o processo do Nó 1 (Ctrl + C), você verá nos terminais da segunda máquina o gatilho automático de reeleição apurando as baterias dos nós restantes e declarando o novo coordenador.