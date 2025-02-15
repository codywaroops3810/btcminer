import os
import sys
import subprocess

# Caminho para o seu script principal
main_script = "btcminer.py"  # Substitua pelo nome do seu script

# Caminho para o ícone (deve ser um arquivo .ico)
icon_path = "btc-miner.ico"  # Substitua pelo caminho para o seu ícone

# Verifica se o arquivo do ícone existe
if not os.path.exists(icon_path):
    print(f"Erro: O arquivo de ícone '{icon_path}' não foi encontrado.")
    sys.exit(1)

# Comando PyInstaller
command = [
    "pyinstaller",
    "--onefile",          # Empacota tudo em um único arquivo
    "--windowed",         # Remove o console (modo janela)
    f"--icon={icon_path}", # Define o ícone personalizado
    "--noconsole",        # Não exibe o console
    main_script           # Seu script principal
]

# Executa o comando PyInstaller
print("Iniciando o processo de criação do executável...")
try:
    subprocess.run(command, check=True)
    print("Executável criado com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Ocorreu um erro ao criar o executável: {e}")