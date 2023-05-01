# -*- encoding: utf-8 -*-

import sys

from lexer import Lexer
from p4rser import Parser
import p4rser

if __name__ == "__main__":
    lexer = Lexer()
    filename = "../examples/test.txt"
    with open(filename) as file:
        content = file.readlines()

    Lexems = lexer.lex(content)
    print(Lexems)
    p4rser = Parser(Lexems)

    ftree, ast = p4rser.parse()

    # Affichage de l'arbre généalogique et de l'AST
    ftree.print_frise()
    ftree.print_tree()

    ast.show_AST()




