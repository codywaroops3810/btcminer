import os
import sys
import hashlib
import ecdsa
from base58 import b58encode_check
import requests
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

def resource_path(relative_path):
    """Obter o caminho correto para recursos quando o script é empacotado como um executável."""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Função para gerar um endereço Bitcoin
def generate_bitcoin_address():
    # Gera uma chave privada aleatória (32 bytes)
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key_bytes = private_key.to_string()

    # Deriva a chave pública a partir da chave privada
    public_key = private_key.get_verifying_key().to_string()
    
    # Converte a chave pública para o formato comprimido
    if public_key[31] % 2 == 0:
        prefix = b'\x02'
    else:
        prefix = b'\x03'
    compressed_public_key = prefix + public_key[1:33]

    # Gera o hash SHA-256 da chave pública comprimida
    sha256_hash = hashlib.sha256(compressed_public_key).digest()

    # Gera o hash RIPEMD-160 do hash SHA-256
    ripemd160_hash = hashlib.new('ripemd160')
    ripemd160_hash.update(sha256_hash)
    ripe_hash = ripemd160_hash.digest()

    # Adiciona o prefixo da rede principal do Bitcoin (0x00)
    network_byte = b'\x00'
    raw_address = network_byte + ripe_hash

    # Codifica o endereço em Base58Check
    bitcoin_address = b58encode_check(raw_address).decode('utf-8')

    return bitcoin_address, private_key_bytes.hex()

# Função para verificar o saldo de um endereço Bitcoin
def check_balance(address):
    url = f"https://blockstream.info/api/address/{address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = int(data.get("chain_stats", {}).get("funded_txo_sum", 0)) / 10**8  # Convert to BTC
            return balance
        else:
            print(f"Falha ao obter informações para o endereço {address}. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao verificar saldo do endereço {address}: {e}")
        return None

# Função para atualizar a interface gráfica com cores
def update_gui(address, balance, text_area):
    message = f"Endereço: {address} | Saldo: {balance:.8f} BTC\n"
    if balance > 0:
        text_area.insert(tk.END, message, "green")  # Aplica a tag "green"
    else:
        text_area.insert(tk.END, message, "red")  # Aplica a tag "red"
    text_area.see(tk.END)  # Rolagem automática

# Função para exibir a mensagem "Created by CodyWaroops"
def display_credits(text_area):
    credits_message = "Created by CodyWaroops\n"
    # Habilita temporariamente o widget Text
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, credits_message, "blue")  # Exibe a mensagem com a cor azul
    text_area.tag_configure("blue", foreground="blue")
    text_area.config(state=tk.DISABLED)  # Desabilita o widget novamente
    text_area.see(tk.END)

# Função principal para gerar endereços e verificar saldos
def generate_addresses(text_area, stop_event):
    while not stop_event.is_set():
        address, private_key = generate_bitcoin_address()
        balance = check_balance(address)
        if balance is not None:
            # Habilita temporariamente o widget Text
            text_area.config(state=tk.NORMAL)
            update_gui(address, balance, text_area)
            text_area.config(state=tk.DISABLED)  # Desabilita o widget novamente
        time.sleep(1)  # Aguarda 1 segundo entre as verificações

# Função para iniciar/pausar a geração de endereços
def toggle_generation(button, stop_event, thread):
    if button["text"] == "Iniciar":
        button["text"] = "Pausar"
        stop_event.clear()  # Limpa o evento de parada
        thread.start()  # Inicia a thread
    else:
        button["text"] = "Iniciar"
        stop_event.set()  # Define o evento de parada

# Configuração da interface gráfica
def main():
    root = tk.Tk()
    root.title("Gerador de Endereços Bitcoin")

    # Defina o ícone da janela usando o caminho correto
    icon_path = resource_path("btc-miner.ico")
    root.wm_iconbitmap(icon_path)

    # Área de texto para exibir os resultados
    text_area = tk.Text(root, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)  # Desabilita edição
    text_area.pack(pady=10)

    # Define tags para cores
    text_area.tag_configure("green", foreground="green")
    text_area.tag_configure("red", foreground="red")
    text_area.tag_configure("blue", foreground="blue")  # Define a tag para a cor azul

    # Variável para controlar a pausa/início
    stop_event = threading.Event()

    # Thread para gerar endereços
    thread = threading.Thread(target=generate_addresses, args=(text_area, stop_event), daemon=True)

    # Botão para iniciar/pausar
    button = tk.Button(root, text="Iniciar", command=lambda: toggle_generation(button, stop_event, thread))
    button.pack(pady=5)

    # Exibe a mensagem "Created by CodyWaroops" na interface gráfica
    display_credits(text_area)

    root.mainloop()

if __name__ == "__main__":
    main()