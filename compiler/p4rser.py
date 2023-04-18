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
        if len(self.parents) >= 2:
            return [self.parents[0].name, self.parents[1].name]
        else:
            return [self.parents[0].name]

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

    def print_tree(self):
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



