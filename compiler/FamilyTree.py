
import graphviz as gv

def format_str_date(date):
    # receive a date in datetime format and return a string
    # Condition to check if the date is not None
    if date is None:
        return ""
    else:
        return date.strftime("%d/%m/%Y")

class FamilyTree:
    """
    Classe représentant un arbre généalogique
    """
    def __init__(self):
        """
        Initialisation d'un arbre généalogique
        """
        self.persons = []
        self.racine = None

    def get_person(self, name):
        """
        Retourne la personne dont le nom est passé en paramètre
        :param name:
        :return:
        """
        for person in self.persons:
            if person.name == name:
                return person
        return None

    def __str__(self):
        """
        Retourne une description de l'arbre généalogique
        :return:
        """
        desc = ""
        for person in self.persons:
            desc += str(person) + "\n"
        return desc

    def print_frise(self):
        """
        Affiche la frise chronologique correspondante à l'arbre
        :return:
        """
        # Lister tous les évènements
        events = {}
        for person in self.persons:
            # Ajout de la naissance
            if person.birthdate not in events.keys():  # Premier ajout de la date
                events[person.birthdate] = ["Naissance de " + person.name + "."]
            else:
                events[person.birthdate].append("Naissance de " + person.name + ".")
            # Ajout de la mort
            if person.deathdate is not None:
                if person.deathdate not in events.keys():
                    events[person.deathdate] = ["† Décès de " + person.name + "."]
                else:
                    events[person.deathdate].append("† Décès de " + person.name + ".")
            # Ajout du mariage
            if person.spouse is not None:
                if person.wedding_date is not None:
                    if person.wedding_date not in events.keys():
                        events[person.wedding_date] = ["♥ Mariage de " + person.name + " et " + person.spouse.name + "."]
                    else:
                        # Retirer les doublons (mariage de A et B, mariage de B et A)
                        if "♥ Mariage de " + person.spouse.name + " et " + person.name + "." not in events[person.wedding_date]:
                            events[person.wedding_date].append("♥ Mariage de " + person.name + " et " + person.spouse.name + ".")


        # Affichage de la frise

        print("###############################\n##### Frise chronologique #####\n###############################\n")
        if self.racine.name[0] in ['A', 'E', 'I', 'O', 'U', 'Y']:
            title_label = f"Arbre généalogique d'{self.racine.name}"
        else:
            title_label = f"Arbre généalogique de {self.racine.name}"
        print(title_label + ".\n")


        # liste contenant les décades déjà affichées
        decades = []
        for date in sorted(events.keys()):
            # Affichage des siècles :
            # Récupération du siècle
            century = date.year // 100
            if century not in decades:
                decades.append(century)
                # Affichage du siècle sur 3 lignes
                print(f"\n###########################\n####### {century}è siècle  #######\n###########################\n")

            # Affichage des decades (sauf celles correspondant aux siècles):
            if date.year % 10 == 0 and date.year not in decades:
                decades.append(date.year)
                print(f"\n========== {date.year} ==========\n")
            # Affichage de la date et du premier évènement
            print(f"{format_str_date(date)} : {events[date][0]}")

            # Affichage des autres évènements
            for event in events[date][1:]:
                print(f"------------ {event}")


    def get_dict_gen(self):
        """
        Retourne un dictionnaire génération : liste des personnes
        :return:
        """

        # on boucle sur toutes les personnes et on constitue le dictionnaire
        dict_gen = {}
        for person in self.persons:
            # Si la génération a déjà été ajoutée
            if person.gen in dict_gen.keys():
                dict_gen[person.gen].append(person)
            else:
                dict_gen[person.gen] = [person]
        return dict_gen

    def get_person_without_generation(self):
        """
        Retourne la liste des personnes dont la génération n'est pas définie
        :return:
        """

        # On boucle sur les personnes
        persons_without_generation = []
        for person in self.persons:
            # Si la personne n'a pas de génération
            if person.gen is None:
                persons_without_generation.append(person)
        return persons_without_generation

    def print_gen(self):
        """
        Affiche les générations de chacun
        :return:
        """
        # On affiche les générations de chacun
        dict_gen = self.get_dict_gen()
        for gen in dict_gen.keys():
            print(f"Génération {gen} :")
            for person in dict_gen[gen]:
                print(f"    {person.name}")

    def print_tree(self):
        """
        Affiche l'arbre généalogique sous la forme d'un graphique
        :return:
        """
        # Créer un nouveau graphique
        graph = gv.Graph(format='png')

        # Ajouter un titre en haut du graphique selon la première lettre du prénom
        if self.racine.name[0] in ['A', 'E', 'I', 'O', 'U', 'Y']:
            title_label = f"Arbre généalogique d'{self.racine.name}"
        else:
            title_label = f"Arbre généalogique de {self.racine.name}"
        graph.attr(label=title_label, labelloc='t', labeljust='c', fontsize='20', fontcolor='blue')

        # On détermine la génération des personnes de l'arbre

        # Créer un dictionnaire contenant la profondeur = génération de chaque personne par parcours de graphe
        dict_successeurs = {}
        # On boucle sur toutes les personnes et on constitue le dictionnaire
        for person in self.persons:
            # On regarde s'il a des successeurs, i.e. des enfants
            if len(person.children) > 0:
                # On ajoute la personne dans le dictionnaire avec comme valeur la liste des enfants
                dict_successeurs[person] = person.children

        # On définit la génération pour chaque personne du graphe
        # Pour la racine, on définit la génération à 0
        self.racine.gen = 0
        # On définit la génération pour tous les parents de manière récursive
        define_parents_generation(self.racine, 1)

        #self.print_gen() A décommenter pour afficher les générations de chacun

        # On trace le graph
        # On boucle sur toutes les personnes par génération et on ajoute les noeuds
        dict_gen = self.get_dict_gen()
        couples_edges_added = [] # liste des couples dont l'arête a déjà été ajoutée
        child_edges_added = [] # liste des enfants dont l'arête a déjà été ajoutée avec leur parent

        n_generations = len(dict_gen.keys())

        for gen in range(n_generations):
            # On ajoute les noeuds
            for person in dict_gen[gen]:
                # Ajouter un noeud pour chaque personne
                # Ajout du noeud de la personne avec ses dates de naissance et de mort
                color = "black"
                # Pour la racine, on met en rouge
                if person == self.racine:
                    color = "red"

                if person.deathdate is not None:
                    graph.node(person.name,label=person.name + "\n" + format_str_date(person.birthdate) + " - " + format_str_date(person.deathdate) + "†", color = color, shape="box")
                else:  # Si la personne est toujours en vie
                    graph.node(person.name, label=person.name + "\n" + format_str_date(person.birthdate) + " - ", color = color, shape="box")

                # Ajout des arêtes pour les couples en rose entre les nœuds de mariage et les personnes mariées
                if person.spouse is not None :
                    couple_name = person.get_couple_names()
                    if couple_name not in couples_edges_added:
                        # Création du noeud de mariage
                        graph.node(couple_name, label="♥ " + format_str_date(person.wedding_date) + " ♥", shape="diamond", color="pink")
                        # Ajout des arêtes entre le noeud de mariage et les personnes du couple
                        graph.edge(person.name, couple_name, color="pink", splines="curved")
                        graph.edge(person.spouse.name, couple_name, color="pink", splines="curved")
                        couples_edges_added.append(couple_name)

                # Ajouter une arête pour chaque enfant
                for child in person.children:
                    if child not in child_edges_added:
                        graph.edge(couple_name, child.name, splines="curved")
                        child_edges_added.append(child)


        # Afficher le graphique
        graph.render('tree', view=True)



def define_parents_generation(enfant,generation_depuis_racine):
    """
    Définit la génération des parents d'un enfant de manière récursive
    :param enfant:
    :param generation_depuis_racine:
    :return:
    """

    # Tant qu'il y a des parents (cas d'arrêt)
    if len(enfant.parents) > 0:
        # On définit la génération des parents
        for parent in enfant.parents:
            parent.gen = generation_depuis_racine

            #On complète pour les frères et soeurs qui n'auraient pas de génération définie
            for child in parent.children:
                if child.gen is None:
                    child.gen = generation_depuis_racine - 1

        # On appelle la fonction pour les parents
        for parent in enfant.parents:
            define_parents_generation(parent, generation_depuis_racine + 1)
