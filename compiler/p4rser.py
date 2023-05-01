# -*- encoding: utf-8 -*-

import logging

import AST
import FamilyTree as FT
from Person import Person

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
            ftree,ast = self.parse_family_tree()
            print("Parsing effectué avec succès")
            return ftree, ast
        except ParsingException as err:
            logger.exception(err)
            raise

    def parse_family_tree(self):
        """
        Parses a family tree which is a succession of statements.
        """
        self.expect("KW_TREE")
        # on créé l'instance d'AST
        global ast
        ast = AST.AST()
        # on crée l'instance d'arbre
        global ftree
        ftree = FT.FamilyTree()
        self.expect("L_CURL_BRACKET")
        while self.show_next().tag != "R_CURL_BRACKET":
            self.parse_stmt(ftree, ast)
        self.expect("R_CURL_BRACKET")

        return ftree, ast

    def parse_stmt(self, tree, ast=None):
        """
        declaration | familial_link | marital_link
        :return:
        """
        next_tag = self.show_next().tag
        if next_tag == "NAME" and self.show_next(n=2).tag == "L_PAREN":
            self.parse_declaration(tree, ast)
        elif next_tag == "NAME" and self.show_next(n=2).tag == "MARITAL_LINK":
            self.parse_marital_link(tree, ast)
        elif next_tag == "NAME" and self.show_next(n=2).tag == "FAMILIAL_LINK":
            self.parse_familial_link(tree, ast)
        else:
            self.error("Expecting declaration, marital_link or familial_link")

    def parse_declaration(self, tree, ast=None):
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
            # Ajout à l'AST
            ast.def_declaration(name, bdate, ddate, racine=True)
        else:
            Person(tree, name, bdate, ddate)
            # Ajout à l'AST
            ast.def_declaration(name, bdate, ddate)

    def parse_familial_link(self, tree, ast=None):
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

    def parse_marital_link(self, tree,ast=None):
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
        # On ajoute sur l'ast
        ast.def_marital_link(spouse1,tree.get_person(spouse1).birthdate, spouse2,tree.get_person(spouse2).birthdate, wedding_date=mdate)

    def error(self, param):
        print(param)
