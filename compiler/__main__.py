# -*- encoding: utf-8 -*-

import sys

from lexer import Lexer
from p4rser import Parser
import p4rser

if __name__ == "__main__":
    lexer = Lexer()
    filename = "../examples/test2.txt"
    with open(filename) as file:
        content = file.readlines()

    Lexems = lexer.lex(content)
    print(Lexems)
    p4rser = Parser(Lexems)

    ftree = p4rser.parse()
    #print_frise(ftree)




