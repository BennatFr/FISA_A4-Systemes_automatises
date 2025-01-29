import cv2
import numpy as np
import requests
from api import CONFIG
# GLOBAL VAR
SNAPSHOT_URL = CONFIG.get("url", "").rstrip("/") + "/webcam/?action=snapshot"


def detect_screws(image_path, annotated_path="screws_detected.jpg"):
    """
    Détecte les vis (cercles) sur l'image et sauvegarde une copie annotée.
    :param image_path: Chemin vers l'image capturée.
    :param annotated_path: Chemin pour sauvegarder l'image annotée.
    :return: Liste des coordonnées des vis détectées (X, Y).
    """
    try:
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print("Erreur : Impossible de charger l'image.")
            return None

        # Convertir en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Augmenter le contraste avec l'égalisation d'histogramme
        gray = cv2.equalizeHist(gray)

        # Appliquer un flou pour réduire le bruit
        blurred = cv2.medianBlur(gray, 5)

        # Détection des cercles avec la transformation de Hough
        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=200,
            param1=40, param2=16, minRadius=6, maxRadius=10
        )

        # Annoter l'image avec les cercles détectés
        annotated_image = image.copy()
        screw_coordinates = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # Dessiner le cercle et son centre
                cv2.circle(annotated_image, (x, y), r, (255, 0, 0), 4)  # Cercle bleu
                cv2.circle(annotated_image, (x, y), 2, (0, 255, 0), 3)  # Centre vert
                screw_coordinates.append((x, y))

        # Sauvegarder l'image annotée
        cv2.imwrite(annotated_path, annotated_image)
        print(f"Image annotée avec les vis détectées sauvegardée sous : {annotated_path}")
        print(f"Vis détectées : {screw_coordinates}")
        return screw_coordinates
    except Exception as e:
        print(f"Erreur lors de la détection des vis : {e}")
        return None


def capture_image(save_path="snapshot.jpg"):
    """
    Capture une image de la caméra connectée à OctoPrint.
    :param save_path: Chemin pour sauvegarder l'image.
    """
    try:
        response = requests.get(SNAPSHOT_URL, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image capturée et sauvegardée sous : {save_path}")
            return save_path
        else:
            print(f"Erreur lors de la capture de l'image. Code : {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la requête à la caméra : {e}")
        return None

def analyze_image(image_path, annotated_path="annotated_image.jpg"):
    """
    Analyse l'image pour détecter les coins et sauvegarde une copie annotée.
    :param image_path: Chemin vers l'image capturée.
    :param annotated_path: Chemin pour sauvegarder l'image annotée.
    :return: Liste des coordonnées des coins (X, Y).
    """
    try:
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print("Erreur : Impossible de charger l'image.")
            return None

        # Convertir en niveaux de gris pour le traitement
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Appliquer un flou pour réduire le bruit
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Détection des bords avec Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Trouver les contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Trouver le plus grand contour (supposé être la pièce)
        largest_contour = max(contours, key=cv2.contourArea)

        # Approximations polygonales pour détecter les coins
        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)

        # Extraire les coordonnées des coins
        corners = [(int(point[0][0]), int(point[0][1])) for point in approx]

        # Annoter l'image avec des points rouges aux coins détectés
        annotated_image = image.copy()
        for idx, (x, y) in enumerate(corners):
            # Dessiner un cercle rouge à chaque coin
            cv2.circle(annotated_image, (x, y), 10, (0, 0, 255), -1)  # Point rouge
            # Ajouter la numérotation des coins
            cv2.putText(
                annotated_image, str(idx + 1), (x + 15, y - 15),  # Position du texte
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2  # Style du texte
            )

        # Sauvegarder l'image annotée
        cv2.imwrite(annotated_path, annotated_image)
        print(f"Image annotée sauvegardée sous : {annotated_path}")

        print(f"Coins détectés : {corners}")
        return corners
    except Exception as e:
        print(f"Erreur lors de l'analyse de l'image : {e}")
        return None