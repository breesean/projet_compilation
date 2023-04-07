# -*- encoding: utf-8 -*-

import logging

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
        self.expect("L_CURL_BRACKET")
        while self.show_next().tag != "R_CURL_BRACKET":
            self.parse_stmt()
        self.expect("R_CURL_BRACKET")

    def parse_stmt(self):
        """
        declaration | familial_link | marital_link
        :return:
        """
        next_tag = self.show_next().tag
        if next_tag == "NAME" and self.show_next(n=2).tag == "L_PAREN":
            self.parse_declaration()
        elif next_tag == "NAME" and self.show_next(n=2).tag == "MARITAL_LINK":
            self.parse_marital_link()
        elif next_tag == "NAME" and self.show_next(n=2).tag == "FAMILIAL_LINK":
            self.parse_familial_link()
        else:
            self.error("Expecting declaration, marital_link or familial_link")


    def parse_declaration(self):
        """
        NAME '(' DATE '-' (DATE)? ')';'
        """
        self.expect("NAME")
        self.expect("L_PAREN")
        self.expect("DATE")
        self.expect("RANGE")
        #La seconde date est facultative, pas besoin de vérifier si elle existe
        self.expect("R_PAREN")
        self.expect("TERMINATOR")

    def parse_familial_link(self):
        """
        NAME '->' NAME ';'
        :return:
        """
        self.expect("NAME")
        self.expect("FAMILIAL_LINK")
        self.expect("NAME")
        self.expect("TERMINATOR")

    def parse_marital_link(self):
        """
        NAME '<=>' NAME ';'
        :return:
        """
        self.expect("NAME")
        self.expect("MARITAL_LINK")
        self.expect("NAME")
        self.expect("TERMINATOR")

    def error(self, param):
        print(param)


class Person:
    def __init__(self,identifier,bdate,ddate):
        self.name = identifier
        self.birthdate = bdate
        self.deathdate = ddate
        self.spouse = None
        self.parent = None

    def __str__(self):
        desc = str(f"{self.name} né le {self.birthdate}")
        if not self.deathdate is None:
            desc += str(f" mort le {self.deathdate} ")
        if not self.spouse is None:
            desc += str(f" marié à {self.spouse.name} ")
        if not self.parent is None:
            desc += str(f" enfant de {self.parent.name}")
        desc += ".\n"
        return desc


#AB = Person("AntoineBREESE","29/05/2001",None)
#print(AB)

