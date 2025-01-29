import cv2
import numpy as np

def detect_screws_interactive(image_path):
    """
    Détection interactive des vis (cercles) sur une image.
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

    # Appliquer une égalisation d'histogramme pour améliorer le contraste
    gray = cv2.equalizeHist(gray)

    # Appliquer un flou médian pour réduire le bruit
    blurred = cv2.medianBlur(gray, 5)

    # Fenêtre interactive pour ajuster les paramètres
    def nothing(x):
        pass

    cv2.namedWindow("Parameters")
    cv2.createTrackbar("dp", "Parameters", 12, 20, nothing)  # dp * 0.1
    cv2.createTrackbar("minDist", "Parameters", 200, 200, nothing)
    cv2.createTrackbar("param1", "Parameters", 90, 300, nothing)
    cv2.createTrackbar("param2", "Parameters", 16, 100, nothing)
    cv2.createTrackbar("minRadius", "Parameters", 6, 50, nothing)
    cv2.createTrackbar("maxRadius", "Parameters", 10, 100, nothing)

    while True:
        # Lire les paramètres depuis les trackbars
        dp = cv2.getTrackbarPos("dp", "Parameters") * 0.1
        minDist = cv2.getTrackbarPos("minDist", "Parameters")
        param1 = cv2.getTrackbarPos("param1", "Parameters")
        param2 = cv2.getTrackbarPos("param2", "Parameters")
        minRadius = cv2.getTrackbarPos("minRadius", "Parameters")
        maxRadius = cv2.getTrackbarPos("maxRadius", "Parameters")

        # Détection des cercles
        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
            param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius
        )

        # Annoter l'image
        annotated_image = image.copy()
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(annotated_image, (x, y), r, (255, 0, 0), 2)  # Cercle bleu
                cv2.circle(annotated_image, (x, y), 2, (0, 255, 0), 3)  # Centre vert

        # Afficher l'image annotée
        cv2.imshow("Detected Screws", annotated_image)

        # Appuyez sur 'ESC' pour quitter
        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()

detect_screws_interactive("snapshot.jpg")
