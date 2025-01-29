import os
import numpy as np
import json
import time

from api import *
from camera_analysis import *
from pe import *
from tools import *

# Charger la configuration
with open("config/config.json", "r") as config_file:
    CONFIG = json.load(config_file)

def analyze_object_and_move():
    """
    Déplace la buse, demande à l'utilisateur de poser l'objet, capture l'image,
    analyse sa position et déplace la buse.
    """
    # Positionner la buse à l'origine (G28) et déplacer à Y250
    print("Initialisation de la position de la buse...")
    g28 = input("Appuyer sur 0 pour G28 & M92 ? : ")
    wait_time = 4
    if(g28 == "0"):
        wait_time = 16
        send_gcode_command("G28")  # Home all axes
        send_gcode_command("M92 E4000 T0") # Set E steps per mm
        send_gcode_command("M83")  # Set E to relative mode
    send_gcode_command("G1 X250 Y250 Z50 F10000")  # Déplacement à Y250

    # Attendre quelques secondes avant de revérifier
    time.sleep(wait_time)

    print("Buse positionnée à Y250. Veuillez placer l'objet sur le plateau.")

    # Demander une confirmation à l'utilisateur avant de capturer l'image
    input("Appuyez sur Entrée une fois que l'objet est correctement positionné.")

    # Capture une image
    image_path = capture_image("snapshot.jpg")
    if not image_path:
        print("Échec de la capture d'image.")
        return

    # Détecter les vis pour ajuster les coordonnées
    screws_image_coords = detect_screws(image_path, "screws_detected.jpg")
    if not screws_image_coords or len(screws_image_coords) < 4:
        print("Échec de la détection des vis ou vis insuffisantes détectées.")
        return

    # Ordonner les vis détectées
    screws_image_coords = order_screws(screws_image_coords)
    print(f"Vis détectées et ordonnées : {screws_image_coords}\n")

    # Coordonnées réelles des vis (en mm, à calibrer pour ton imprimante)
    screws_real_coords = [
        (242, 38),  # Top left
        (72, 38),   # Top right
        (242, 210), # Bottom left
        (71, 208)   # Bottom right
    ]

    # Calculer la transformation pixel -> mm
    transform_matrix = compute_pixel_to_mm_transformation(screws_image_coords, screws_real_coords)

    # Détecter les coins de l'objet (en pixels)
    corners_image_coords = analyze_image(image_path, "annotated_image.jpg")
    if not corners_image_coords:
        print("Échec de l'analyse de l'image pour détecter les coins.")
        return

    print(f"Coins détectés (pixels) : {corners_image_coords}")

    # Transformer les coins de l'objet en mm
    corners_real_coords = transform_coordinates(corners_image_coords, transform_matrix)
    print(f"Coins de l'objet (mm) : {corners_real_coords}")

    # Ajuster les coins pour aller à l'intérieur de l'objet
    adjusted_corners = adjust_corners_for_interior(corners_real_coords, offset=5)
    print(f"Coins ajustés (mm) : {adjusted_corners}\n")

    # Aller rapidement au-dessus du premier coin ajusté
    x_first, y_first = adjusted_corners[0]
    send_gcode_command(f"G1 X{x_first:.2f} Y{y_first:.2f} Z10 F3000")  # Déplacement rapide

    input("Appuyez sur Entrée pour continuer et déplacer la buse aux coins de l'objet.")

    # Déplacer la buse aux coins ajustés de l'objet
    extrusion_percentage = 50  # Pourcentage du trajet où E4 est activé

    for idx in range(len(adjusted_corners)):
        if(idx==3):
            continue
        if(idx%2==0):
            E_value = 4
        else:
            E_value = 2
        # Point de départ
        x_start, y_start = adjusted_corners[idx]
        # Point d'arrivée (prochain coin ou retour au premier coin)
        x_end, y_end = adjusted_corners[(idx + 1) % len(adjusted_corners)]

        print(f"Déplacement avec extrusion de {x_start:.2f}, {y_start:.2f} vers {x_end:.2f}, {y_end:.2f}")

        # Calculer le point où l'extrusion doit s'arrêter
        x_extrude = x_start + (x_end - x_start) * (extrusion_percentage / 100)
        y_extrude = y_start + (y_end - y_start) * (extrusion_percentage / 100)

        # Déplacement avec extrusion (E3 activé)
        send_gcode_command(f"G1 X{x_extrude:.2f} Y{y_extrude:.2f} Z6 F400 E{E_value}")
        print(f"Extrusion active jusqu'à : X={x_extrude:.2f}, Y={y_extrude:.2f}")

        # Compléter le déplacement sans extrusion
        send_gcode_command(f"G1 X{x_end:.2f} Y{y_end:.2f} Z6 F200")
        print(f"Déplacement sans extrusion jusqu'à : X={x_end:.2f}, Y={y_end:.2f}")

    send_gcode_command("G1 X250 Y250 Z50 F10000") # Retour à la position initiale

GCODE_FOLDER = CONFIG["gcode_folder"]

if __name__ == "__main__":
    print("Bienvenue dans l'application OctoPrint G-code Sender!")

    # Vérifiez si l'imprimante est connectée
    if not is_printer_connected():
        print("L'imprimante n'est pas connectée. Tentative de connexion...")
        connect_printer()

        # Attendre quelques secondes avant de revérifier
        time.sleep(2)

    # Vérifiez à nouveau après la tentative de connexion
    if not is_printer_connected():
        print("Impossible de se connecter à l'imprimante. Vérifiez l'état de l'imprimante et d'OctoPrint.")

    # Keep the main menu running
    while True:
        print("====================================")
        print("1. Envoyer une commande G-code")
        print("2. Envoyer un fichier G-code")
        print("3. Analyser l'objet et déplacer la buse")
        print("4. Séquence de PE")
        print("====================================")
        
        choice = input("Sélectionnez une option (1/2/3/4) : ")
        print("\n")
        
        # Process the user choice
        if choice == "1":
            command = input("Entrez la commande G-code : ")
            send_gcode_command(command)
        elif choice == "2":
            files = list_gcode_files()
            if not files:
                print("Aucun fichier G-code disponible.")
            else:
                print("Fichiers disponibles :")
                for idx, file in enumerate(files):
                    print(f"{idx + 1}. {file}")
                
                file_choice = input("Sélectionnez un fichier (numéro) : ")
                try:
                    file_index = int(file_choice) - 1
                    if 0 <= file_index < len(files):
                        filepath = os.path.join(GCODE_FOLDER, files[file_index])
                        send_gcode_file(filepath)
                    else:
                        print("Choix invalide.")
                except ValueError:
                    print("Entrée invalide.")
        if choice == "3":
            analyze_object_and_move()
        if choice == "4":
            pe()
        if(choice == "9"):
            print("Fermeture de l'application.")
            break
        else:
            print("Option invalide.")
