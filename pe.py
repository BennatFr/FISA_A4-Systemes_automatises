from api import *
import time

# GLOBAL VAR

x_start = 100
y_start = 15

x_pas = 0
y_pas = 10

X = 50

V_x = [200, 600]
e_X = [0.01, 0.75] 
h = [0.1 , 1]

sequences = [
    [0,0,0],
    [1,0,0],
    [0,1,0],
    [1,1,0],
    [0,0,1],
    [1,0,1],
    [0,1,1],
    [1,1,1],
]

def pe():
    """
    Fonction principale pour lancer le Pattern Experiment (PE).
    """
    # Define the global variables
    global x_start, y_start

    if pe_verif() == False:
        return False
    send_gcode_command("G28")  # Home all axes
    send_gcode_command("M92 E4000 T0") # Set E steps per mm
    send_gcode_command("M83")  # Set E to relative mode

    time.sleep(8)

    for i, s in enumerate(sequences):
        print("====================================")
        print("Sequence N° : ", i)
        print("V_x (", str(s[0]).replace("0","-1"), ") : ", V_x[s[0]])
        print("e_X (", str(s[1]).replace("0","-1"), ") : ", e_X[s[1]])
        print("h (", str(s[2]).replace("0","-1"), ") : ", h[s[2]])
        input("Press Enter to continue...")
        print("====================================")
        pe_pos(x_start, y_start, h[s[2]])
        E = e_X[s[1]] * X
        pe_col(x_start, y_start, h[s[2]], V_x[s[0]], E, X)

        x_start += x_pas
        y_start += y_pas

def pe_verif():
    """
    Vérifie si les paramètres de départ sont corrects.
    :return: True si les paramètres sont valides, False sinon. 
    """
    if(x_start < 50):
        print("Position de départ inférieure à 50mm en X => En dehors de la zone de travail")
        return False
    if(y_start <= 10):
        print("Position de départ inférieure à 10mm en Y => En dehors de la zone de travail")
        return False
    if(x_start >= 250 or y_start >= 250):
        print("Position de départ supérieure à 250mm => En dehors de la zone de travail")
        return False
    if(x_start + (X*2) >= 250):
        print("Dépassement de la zone de travail en X")
        return False

def pe_pos(x, y, z):
    """
    Déplace la tête d'impression à la position spécifiée.
    :param x: Coordonnée X
    :param y: Coordonnée Y
    :param z: Coordonnée Z
    """
    send_gcode_command("G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F2000")

def pe_col(x, y, z, v, e, X):
    """
    Réalise une colonne de Pattern Experiment (PE). 
    :param x: Coordonnée X de départ
    :param y: Coordonnée Y de départ
    :param z: Coordonnée Z de départ
    :param v: Vitesse de déplacement
    :param e: Distance de déplacement en E
    """
    send_gcode_command("G1 X" + str(x + X) + " Y" + str(y) + " Z" + str(z) + " E" + str(e) + " F" + str(v))
    send_gcode_command("G1 X" + str(x + (X *2)) + " Y" + str(y) + " Z" + str(z) + " F" + str(v))
    send_gcode_command("G1 X" + str(x + (X *2)) + " Y" + str(y) + " Z7" + " F2000")
