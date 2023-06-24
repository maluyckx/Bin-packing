#!/usr/bin/python
"""
Projet d'INFO-F310
Algorithmique et recherche opérationnelle
Programme linéaire pour le bin packing

Luyckx Marco - 496283
Marques Correia Tiago - 495305
"""

import sys
import os
import binpacking

class generate_model:
    def __init__(self, argv):
        """
        Cette fonction fait le parsing du fichier donné en entrée.
        """
        
        #print("Total arguments passed: ", len(sys.argv))
        if len(sys.argv) != 3:
            print("#### ERROR #### \n Vous n'avez pas donné le nombre correct d'arguments !\n###############")
            exit(0)

        #print("Nom du fichier : " + sys.argv[1] + " et P: " + sys.argv[2])
        self.nom_fichier = sys.argv[1]
        self.p = int(sys.argv[2])

        with open(self.nom_fichier) as f:
            lines = f.readlines()
            for i in range(len(lines)):
                lines[i] = lines[i].replace("\n","").split()
        #print(lines)
        self.nb_objet_total = int(lines[0][0]) # nombre total de produits
        self.t = int(lines[0][1])  # nombre de type de produits
        self.i = int(lines[0][2])  # nombre d'incompatibilités
        self.c = int(lines[1][0])  # capacité totale des boîtes 
        self.id = self.nom_fichier[len(self.nom_fichier)-5:len(self.nom_fichier)-4]

        self.liste_s_n_b = []  # liste des types de produits et de leurs tailles
        for k in range(self.t):
            for j in range(len(lines [k+2])):
                lines[k+2][j] = int(lines[k+2][j])
            self.liste_s_n_b.append(lines [k+2])
        #print(self.liste_s_n_b)

        self.liste_incompatibilite = [] # liste des incompatibilités
        for k in range(self.i):
            for j in range(len(lines [k+2+self.t])):
                lines[k+2+self.t][j] = int(lines[k+2+self.t][j])
            self.liste_incompatibilite.append(lines[k+2+self.t])
        #print(self.liste_incompatibilite)
        
        self.max_boite = 0 # le nombre maximum de boite = nombre total de produits qu'on doit ranger
        self.bigM = 0
        for i in range(len(self.liste_s_n_b)):
            self.max_boite += self.liste_s_n_b[i][1]
            if (self.bigM < self.liste_s_n_b[i][1]): # la quantité la plus grand parmi les types de produits
                self.bigM = self.liste_s_n_b[i][1]        

        nom_fichier_output = "model_" + str(self.nb_objet_total) + "_" + str(self.t) + "_" + str(self.i) + "_" + str(self.id) + "_" + str(self.p) 
        self.nom_fichier_output_lp = nom_fichier_output + ".lp"
        self.nom_fichier_output_sol = nom_fichier_output + ".sol"

        self.p_number()

    def heuristiqueP0(self):  
        """
        Fonction heuristique que nous utilisions avant, mais après discussion avec Monsieur De Boeck, 
        nous avons choisi d'implémenter notre propre fonction qui se trouve juste en dessous (greedy())
        """
        allObjects = []
        for i in range(len(self.liste_s_n_b)):
            for j in range(self.liste_s_n_b[i][1]):
                allObjects.append(self.liste_s_n_b[i][0])

        bins = binpacking.to_constant_volume(allObjects,self.c)
        self.max_boite = len(bins)


    def greedy(self): 
        """
        Fonction heuristique implémentée par nos soins.
        Nous nous sommes basés sur ce pseudo-ci : https://bastian.rieck.me/research/Note_BP.pdf
        """
        liste_poids = []
        for i in range(len(self.liste_s_n_b)):
            for j in range(self.liste_s_n_b[i][1]):
                liste_poids.append(self.liste_s_n_b[i][0])

        nombre_boite = 0
        boites_restantes = [0]* len(liste_poids)

        i = 0
        while i < len(liste_poids): 
            minimum = self.c + 1
            meilleur_index = 0
            j = 0
            while j < nombre_boite: 
                if (boites_restantes[j] >= liste_poids[i] and boites_restantes[j] - liste_poids[i] < minimum):
                    meilleur_index = j
                    minimum = boites_restantes[j] - liste_poids[i]
                j += 1

            if (minimum == self.c + 1): # On doit rajouter une boîte supplémentaire
                boites_restantes[nombre_boite] = self.c - liste_poids[i]
                nombre_boite += 1
            else: 
                boites_restantes[meilleur_index] -= liste_poids[i]

            i += 1

        self.max_boite = nombre_boite

    def p_number(self): 
        """
        Fonction qui crée le fichier du modèle.
        """
        ## Les listes ci-dessous contiendront l'ensemble des variables de décision associés
        listeY = []
        listeX = []
        listeZ = []
        if self.p == 0:
            #self.heuristiqueP0()
            self.greedy()
        
        for i in range(self.max_boite):
            listeY.append("y_" + str(i))
        for t in range(self.t):
            for b in range(self.max_boite):
                listeX.append("x_" + str(b) + "_" + str(t))
        if self.p == 1 or self.p == 2:
            for t in range(self.t):
                for b in range(self.max_boite):
                    listeZ.append("z_" + str(b) + "_" + str(t))
    
        ##objectif
        objectif = ""
        for i in range(self.max_boite):
            objectif += "y_" + str(i) + " + "
        objectif = objectif[:-2]

        ##subject to
        constraints = ""
        for t in range(self.t):  ## voir Rapport.pdf : contrainte (2)
            constraints += "\tc_obj_" + str(t) + ": "
            for b in range(self.max_boite):
                constraints += "x_" + str(b) + "_" + str(t) + " + "
            constraints = constraints[:-2]
            constraints += "= " + str(self.liste_s_n_b[t][1]) + "\n"

        for b in range(self.max_boite):      ## voir Rapport.pdf : contrainte (3)
            constraints += "\tc_limit_" + str(b) + ": "
            for t in range(self.t):
                constraints += str(self.liste_s_n_b[t][0]) + " x_" + str(b) + "_" + str(t) + " + "
            constraints = constraints[:-2]
            constraints += "- " +  str(self.c) + " y_" + str(b) + " <= " + "0 \n"
        constraints = constraints[:-1]

        if self.p == 1 or self.p == 2:
            constraints += " \n"
            for element in range(len(listeX)):    ## voir Rapport.pdf : contrainte (4)
                constraints +=  "\tc_bigM_" + str(element) + ": " + listeX[element] + " - " +str(self.bigM)+ " " + listeZ[element]+ " <= 0 \n"

            for element in range(len(listeX)):   ## voir Rapport.pdf : contrainte (5)
                constraints +=  "\tc_less_" + str(element) + ": " + listeZ[element] + " - " + listeX[element]+ " <= 0 \n"

            for t in range(self.t):    ## voir Rapport.pdf : contrainte (6)
                constraints += "\tc_maxobjects_" + str(t) + ": "
                for b in range(self.max_boite):
                    constraints +=  "z_" + str(b) +  "_" + str(t) + " + "
                constraints = constraints[:-2]
                constraints += " <= " + str(self.liste_s_n_b[t][2]) + "\n"
            constraints = constraints[:-1]

        if self.p == 2 :
            constraints += " \n"
            compteur = 0   
            for incomp in self.liste_incompatibilite:    ## voir Rapport.pdf : contrainte (7)
                for b in range(self.max_boite):
                    constraints += "\tc_incomp_" + str(compteur) + ": "
                    compteur+=1
                    for element in incomp:  # for element in range(len(incomp)):   
                        constraints +=  "z_" + str(b) +  "_" + str(element) + " + "  # incomp[element]
                    constraints = constraints[:-2]
                    constraints += " <= 1 \n"
            constraints = constraints[:-1] 

        with open(self.nom_fichier_output_lp, "w") as file: 
            file.write("\\ " + self.nom_fichier + " | " + self.nom_fichier_output_lp)
            file.write("\n \nMinimize \n \tobj: " + objectif) 
            file.write("\nSubject To\n")
            # contraintes ici
            file.write(constraints)
            file.write("\nBounds\n")
            for i in range(len(listeX)):    ## voir Rapport.pdf : contrainte (8)
                file.write("\t" + str(listeX[i]) + " >= 0\n")
            file.write("\nBinary\n")
            for i in range(len(listeY)):    ## voir Rapport.pdf : contrainte (9)
                file.write("\t" + str(listeY[i]) + "\n")
            if self.p == 1 or self.p == 2:
                for i in range(len(listeZ)):    ## voir Rapport.pdf : contrainte (10)
                    file.write("\t" + str(listeZ[i]) + "\n")
            file.write("\nInteger\n")
            for i in range(len(listeX)):
                file.write("\t" + str(listeX[i]) + "\n")
            file.write("\nEnd")

        #os.system("glpsol --lp " + "testo_refactoring/" + self.nom_fichier_output_lp + " -o " + "testo_refactoring/" + self.nom_fichier_output_sol + " --tmlim 600")
        # la ligne ci-dessus nous permettait de lancer directement la commande qui résoud le modèle créé.

generate_model(sys.argv[1:])



