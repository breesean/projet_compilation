# -*- encoding: utf-8 -*-

import logging
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import graphviz as gv
import random

logger = logging.getLogger(__name__)


class ParsingException(Exception):
    pass


class Parser:
    def __init__(self, lexems):
        """
        Component in charge of syntaxic analysis.
        """
        self.lexems = lexems

    # ==========================
    #      Helper Functions
    # ==========================

    def accept(self):
        """
        Pops the lexem out of the lexems list.
        """
        self.show_next()
        return self.lexems.pop(0)

    def show_next(self, n=1):
        """
        Returns the next token in the list WITHOUT popping it.
        """
        try:
            return self.lexems[n - 1]
        except IndexError:
            self.error("No more lexems left.")

    def expect(self, tag):
        """
        Pops the next token from the lexems list and tests its type through the tag.
        """
        next_lexem = self.show_next()
        if next_lexem.tag != tag:
            raise ParsingException(
                f"ERROR at {str(self.show_next().position)}: Expected {tag}, got {next_lexem.tag} instead"
            )
        return self.accept()

    def remove_comments(self):
        """
        Removes the comments from the token list by testing their tags.
        """
        self.lexems = [lexem for lexem in self.lexems if lexem.tag != "COMMENT"]

    # ==========================
    #     Parsing Functions
    # ==========================

    def parse(self):
        """
        Main function: launches the parsing operation given a lexem list.
        """
        try:
            self.remove_comments()
            self.parse_family_tree()
            print("Parsing effectué avec succès")
        except ParsingException as err:
            logger.exception(err)
            raise

    def parse_family_tree(self):
        """
        Parses a family tree which is a succession of statements.
        """
        self.expect("KW_TREE")
        # on crée l'instance d'arbre
        global ftree
        ftree = FamilyTree()
        self.expect("L_CURL_BRACKET")
        while self.show_next().tag != "R_CURL_BRACKET":
            self.parse_stmt(ftree)
        self.expect("R_CURL_BRACKET")
        ftree.print_frise()
        ftree.print_tree()

        return ftree

    def parse_stmt(self, tree):
        """
        declaration | familial_link | marital_link
        :return:
        """
        next_tag = self.show_next().tag
        if next_tag == "NAME" and self.show_next(n=2).tag == "L_PAREN":
            self.parse_declaration(tree)
        elif next_tag == "NAME" and self.show_next(n=2).tag == "MARITAL_LINK":
            self.parse_marital_link(tree)
        elif next_tag == "NAME" and self.show_next(n=2).tag == "FAMILIAL_LINK":
            self.parse_familial_link(tree)
        else:
            self.error("Expecting declaration, marital_link or familial_link")

    def parse_declaration(self, tree):
        """
        NAME '(' DATE '-' (DATE)? ')';'
        """
        name = self.expect('NAME').value  # on récupère le nom de la personne
        self.expect("L_PAREN")
        bdate = self.expect("DATE").value  # on récupère la date de naissance
        self.expect("RANGE")
        # La seconde date est facultative, pas besoin de vérifier si elle existe
        if self.show_next().tag == "DATE":
            ddate = self.expect("DATE").value  # on récupère la date de décès
        else:
            ddate = None
        self.expect("R_PAREN")
        self.expect("TERMINATOR")
        # On crée l'objet Person
        # Si c'est la première personne de l'arbre, on la définit comme racine
        if tree.racine is None:
            tree.racine = Person(tree, name, bdate, ddate)
        else:
            Person(tree, name, bdate, ddate)

    def parse_familial_link(self, tree):
        """
        NAME '->' NAME ';'
        :return:
        """
        name_parent = self.expect('NAME').value  # on récupère le nom de la personne
        self.expect("FAMILIAL_LINK")
        name_child = self.expect("NAME").value  # on récupère le nom de la personne
        self.expect("TERMINATOR")

        # On crée le lien
        tree.get_person(name_parent).define_familial_link(tree.get_person(name_child))

    def parse_marital_link(self, tree):
        """
        NAME '<=>' NAME ';'
        :return:
        """
        spouse1 = self.expect('NAME').value  # on récupère le nom de la personne
        self.expect("MARITAL_LINK")
        spouse2 = self.expect("NAME").value  # on récupère le nom de la personne
        #On prend en compte la date du mariage si elle est définie
        if self.show_next().tag == "L_PAREN":
            self.expect("L_PAREN")
            mdate = self.expect("DATE").value
            self.expect("R_PAREN")
        else:
            mdate = None
        self.expect("TERMINATOR")
        # On crée le lien
        tree.get_person(spouse1).define_mariage_link(tree.get_person(spouse2), mdate)

    def error(self, param):
        print(param)


def format_str_date(date):
    # receive a date in datetime format and return a string
    return date.strftime("%d/%m/%Y")


class Person:
    def __init__(self, f_tree, identifier, bdate, ddate):
        self.name = identifier
        # enregistrer la date de naissance au format datetime
        if bdate is not None:
            self.birthdate = datetime.strptime(bdate, "%d/%m/%Y")
        # enregistrer la date de décès au format datetime
        if ddate is not None:
            self.deathdate = datetime.strptime(ddate, "%d/%m/%Y")
        else:
            self.deathdate = None
        self.spouse = None
        self.wedding_date = None
        self.parents = []
        self.children = []
        self.gen = None
        f_tree.persons.append(self)

    def __str__(self):
        desc = str(f"{self.name} né le {format_str_date(self.birthdate)}")
        if not self.deathdate is None:
            desc += str(f" mort le {format_str_date(self.deathdate)}")
        if not self.spouse is None:
            desc += str(f" marié à {self.spouse.name}")
        # si la liste des parents n'est pas vide
        if self.parents!=[]:
          desc += str(f" enfant de {self.get_parents_name()}")
        desc += ".\n"
        return desc

    def get_parents_name(self):
        """
        Retourne le nom des parents ordonnés par ordre alphabétique
        :return:
        """
        if len(self.parents) >= 2:
            if self.parents[0].name < self.parents[1].name:
                return [self.parents[0].name, self.parents[1].name]
            else:
                return [self.parents[1].name, self.parents[0].name]
        else:
            return [self.parents[0].name]


    def get_couple_names(self):
        """
        Retourne le nom des mariés du couple ordonnés par ordre alphabétique
        :return:
        """
        if self.name < self.spouse.name:
            return str(self.name + self.spouse.name)
        else:
            return str(self.spouse.name + self.name)

    def define_mariage_link(self, spouse, wdate):
        self.spouse = spouse
        spouse.spouse = self
        # On met à jour les dates de mariage
        if wdate is not None:
            self.wedding_date = datetime.strptime(wdate, "%d/%m/%Y")
            spouse.wedding_date = datetime.strptime(wdate, "%d/%m/%Y")
        # Sinon, pas besoin, par défaut None lors de l'initialisation

    def define_familial_link(self, child):
        self.children.append(child)
        if self.spouse is not None:
            self.spouse.children.append(child)
        child.parents.append(self)
        child.parents.append(self.spouse)




class FamilyTree:
    def __init__(self):
        self.persons = []
        self.racine = None

    def get_person(self, name):
        for person in self.persons:
            if person.name == name:
                return person
        return None

    def __str__(self):
        print("Arbre de qualité")
        desc = ""
        for person in self.persons:
            desc += str(person) + "\n"
        return desc

    def print_frise(self):
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
        print(f"Arbre généalogique de {self.racine.name}.\n")

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

    def print_old_tree(self):
        """
        Affiche l'arbre généalogique sous la forme d'un graphique
        :return:
        """
        # Créer un nouveau graphique
        graph = gv.Graph(format='png')

        # Créer un dictionnaire contenant la profondeur = génération de chaque personne par parcours de graphe
        # On part de la racine (personne sans parents)
        # On parcourt les enfants de la racine, puis les enfants de ces enfants, etc.


        # Ajouter un noeud de mariage sans label en forme de points pour chaque couple marié

        # liste des couples dont l'arête a déjà été ajoutée
        couples_edges_added = []
        for person in self.persons:
            #Ajout du noeud de la personne avec ses dates de naissance et de mort
            if person.deathdate is not None:
                graph.node(person.name, label= person.name + "\n" + format_str_date(person.birthdate) + " - " + format_str_date(person.deathdate) +"†", shape="box")
            else : # Si la personne est toujours en vie
                graph.node(person.name, label= person.name + "\n" + format_str_date(person.birthdate) + " - ", shape="box")

            # Ajout des arêtes pour les couples en rose entre les nœuds de mariage et les personnes mariées
            if person.spouse is not None and person.spouse not in couples_edges_added and person not in couples_edges_added:
                # Création du noeud de mariage
                graph.node(person.name + person.spouse.name, label="♥ " + format_str_date(person.wedding_date) + " ♥", shape="diamond", color="pink")
                couples_edges_added.append(person)
                couples_edges_added.append(person.spouse)

            # Ajouter les arêtes en partant de la génération 2
            if len(person.parents) == 2:
                print(person.parents[0].name + person.parents[1].name)
                if 1 == 1:
                    # Trouver quel noeud de mariage correspond aux parents
                    ed = person.parents[0].name + person.parents[1].name
                    if ed not in graph.body:
                        ed = person.parents[0].name + person.parents[1].name
                    graph.edge(person.name,ed, splines="curved")

                    # Ajouter l'arête entre le noeud de mariage et la personne
                    # Ajouter les arêtes entre le noeud de mariage et les 2 parents
                    graph.edge(person.parents[0].name,ed, color="red",splines="curved")
                    graph.edge(person.parents[1].name,ed, color="red",splines="curved")




        # Afficher le graphique
        graph.render('tree', view=True)

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

        # Ajouter un titre en haut du graphique
        graph.attr(label=f'Arbre généalogique de {self.racine.name}', labelloc='t', labeljust='c', fontsize='20', fontcolor='blue')

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

        self.print_gen()

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










