import cv2
import numpy as np

def detect_corners_interactive(image_path):
    """
    Détection interactive des coins (points) sur une image.
    Permet de régler les paramètres en temps réel pour améliorer la détection.
    :param image_path: Chemin de l'image à analyser.
    """
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print("Erreur : Impossible de charger l'image.")
        return

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un flou pour réduire le bruit
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Créer une fenêtre interactive pour régler les paramètres
    def nothing(x):
        pass

    cv2.namedWindow("Parameters")
    cv2.createTrackbar("Canny Threshold1", "Parameters", 50, 255, nothing)
    cv2.createTrackbar("Canny Threshold2", "Parameters", 150, 255, nothing)
    cv2.createTrackbar("Epsilon (%)", "Parameters", 2, 10, nothing)  # % de l'arc longueur
    cv2.createTrackbar("Min Area", "Parameters", 100, 1000, nothing)  # Aire min des contours

    while True:
        # Lire les paramètres interactifs
        threshold1 = cv2.getTrackbarPos("Canny Threshold1", "Parameters")
        threshold2 = cv2.getTrackbarPos("Canny Threshold2", "Parameters")
        epsilon_percent = cv2.getTrackbarPos("Epsilon (%)", "Parameters") / 100
        min_area = cv2.getTrackbarPos("Min Area", "Parameters")

        # Appliquer la détection des bords avec Canny
        edges = cv2.Canny(blurred, threshold1, threshold2)

        # Trouver les contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrer les contours par aire et approximer les coins
        corners = []
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:
                epsilon = epsilon_percent * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                corners.extend([(point[0][0], point[0][1]) for point in approx])

        # Annoter l'image avec les coins détectés
        annotated_image = image.copy()
        for idx, (x, y) in enumerate(corners):
            cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)  # Point vert
            cv2.putText(
                annotated_image, str(idx + 1), (x + 10, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )

        # Afficher l'image avec les coins détectés
        cv2.imshow("Detected Corners", annotated_image)

        # Appuyez sur 'ESC' pour quitter
        key = cv2.waitKey(1)
        if key == 27:  # ESC pour quitter
            break

    cv2.destroyAllWindows()

# Exemple d'appel
detect_corners_interactive("snapshot.jpg")