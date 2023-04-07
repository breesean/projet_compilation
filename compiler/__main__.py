# -*- encoding: utf-8 -*-

import sys

from lexer import Lexer
from p4rser import Parser

if __name__ == "__main__":
    lexer = Lexer()
    filename = "../examples/test.txt"
    with open(filename) as file:
        content = file.readlines()

    Lexems = lexer.lex(content)
    print(Lexems)
    p4rser = Parser(Lexems)
    p4rser.parse()

