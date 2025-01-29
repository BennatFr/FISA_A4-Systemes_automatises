import requests
import json

# Charger la configuration
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

# GLOBAL VARIABLES
URL = CONFIG["url"]
API_KEY = CONFIG["api_key"]

def connect_printer():
    """
    Se connecte à l'imprimante via OctoPrint.
    """
    url = URL + "/api/connection"
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "command": "connect",
        "port": "AUTO",
        "baudrate": 0,  # 0 pour sélectionner automatiquement la vitesse
        "printerProfile": "_default"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 204:
            print("Successfully connected to the printer.")
        else:
            print(f"Failed to connect. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error during connection request: {e}")

def is_printer_connected():
    """
    Vérifie si l'imprimante est connectée.
    :return: True si connectée, False sinon.
    """
    url = URL + "/printer"
    headers = {"X-Api-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            state = response.json().get("state", {}).get("flags", {})
            return state.get("operational", False)
        else:
            print(f"Failed to fetch printer state. Status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error during state request: {e}")
        return False


def get_printer_state():
    """
    Vérifie l'état de l'imprimante.
    :return: État de l'imprimante (str)
    """
    headers = {"X-Api-Key": API_KEY}
    try:
        response = requests.get(URL + "/api/printer", headers=headers)
        if response.status_code == 200:
            state = response.json().get("state", {}).get("text", "Unknown")
            return state
        else:
            print(f"Failed to fetch printer state. Status code: {response.status_code}")
            return "Unknown"
    except requests.RequestException as e:
        print(f"Error during state request: {e}")
        return "Unknown"

def send_gcode_command(command):
    """
    Envoie une commande G-code à OctoPrint.
    :param command: Commande G-code à envoyer (str)
    """

    state = get_printer_state()
    if state != "Operational":
        print(f"Printer is not operational. Current state: {state}")
        return

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "command": command
    }
    
    try:
        response = requests.post(URL + "/api/printer/command", json=data, headers=headers)
        if response.status_code == 204:
            print(f"Command '{command}' sent successfully.")
        else:
            print(f"Failed to send command. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error during API request: {e}")

def send_gcode_file(filepath):
    """
    Envoie un fichier G-code ligne par ligne à OctoPrint.
    :param filepath: Chemin vers le fichier G-code (str)
    """
    state = get_printer_state()
    if state != "Operational":
        print(f"Printer is not operational. Current state: {state}")
        return

    try:
        with open(filepath, "r") as file:
            for line in file:
                command = line.strip()
                if command:
                    send_gcode_command(command)
    except FileNotFoundError:
        print(f"File not found: {filepath}")