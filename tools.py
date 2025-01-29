import cv2
import json


# Charger la configuration
with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)

def compute_pixel_to_mm_transformation(image_coords, real_coords):
    """
    Calcule la transformation linéaire pour convertir les pixels en mm.
    :param image_coords: Liste des coordonnées des vis dans l'image (pixels).
    :param real_coords: Liste des coordonnées des vis réelles (mm).
    :return: Matrice de transformation (pixels -> mm).
    """
    # Conversion des listes en matrices pour simplifier les calculs
    image_matrix = np.array(image_coords, dtype=np.float32)
    real_matrix = np.array(real_coords, dtype=np.float32)

    # Trouver la matrice de transformation affine (pixels -> mm)
    transform_matrix = cv2.getPerspectiveTransform(image_matrix, real_matrix)
    return transform_matrix

def transform_coordinates(coords, transform_matrix):
    """
    Transforme des coordonnées à l'aide de la matrice de transformation.
    :param coords: Liste de points à transformer.
    :param transform_matrix: Matrice de transformation (pixels -> mm).
    :return: Liste des points transformés.
    """
    coords = np.array(coords, dtype=np.float32)
    coords = np.concatenate([coords, np.ones((len(coords), 1))], axis=1)  # Ajouter une dimension homogène
    transformed_coords = transform_matrix @ coords.T
    transformed_coords /= transformed_coords[2]  # Normaliser
    return transformed_coords[:2].T

def order_screws(screws_image_coords):
    """
    Ordonne les vis détectées dans l'image en suivant l'ordre :
    Top left, Top right, Bottom left, Bottom right.
    :param screws_image_coords: Liste des coordonnées des vis en pixels [(x1, y1), (x2, y2), ...].
    :return: Liste ordonnée des vis.
    """
    # Trier par l'axe Y (du haut vers le bas)
    screws_image_coords = sorted(screws_image_coords, key=lambda coord: coord[1])

    # Séparer les vis du haut et du bas
    top_screws = sorted(screws_image_coords[:2], key=lambda coord: coord[0])  # Trier par X (gauche à droite)
    bottom_screws = sorted(screws_image_coords[2:], key=lambda coord: coord[0])  # Trier par X (gauche à droite)

    # Retourner les vis dans l'ordre : Top left, Top right, Bottom left, Bottom right
    return [top_screws[0], top_screws[1], bottom_screws[0], bottom_screws[1]]

def adjust_corners_for_interior(corners, offset=5):
    """
    Ajuste les coins pour déplacer la buse à l'intérieur de l'objet.
    :param corners: Liste des coordonnées des coins en mm [(x1, y1), (x2, y2), ...].
    :param offset: Distance en mm pour déplacer les coins vers l'intérieur.
    :return: Liste des coins ajustés.
    """
    # Coins ajustés
    adjusted_corners = []

    for idx, (x, y) in enumerate(corners):
        if idx == 0:  # Top left
            adjusted_corners.append((x + offset, y + offset))
        elif idx == 1:  # Top right
            adjusted_corners.append((x - offset, y + offset))
        elif idx == 2:  # Bottom right
            adjusted_corners.append((x - offset, y - offset))
        elif idx == 3:  # Bottom left
            adjusted_corners.append((x + offset, y - offset))

    return adjusted_corners

def list_gcode_files():
    """
    Liste les fichiers G-code disponibles dans le dossier défini.
    :return: Liste des fichiers G-code (list)
    """
    try:
        return [f for f in os.listdir(GCODE_FOLDER) if f.endswith(".gcode")]
    except FileNotFoundError:
        print(f"G-code folder not found: {GCODE_FOLDER}")
        return []