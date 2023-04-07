# -*- encoding: utf-8 -*-

import pytest

from compiler.lexer import Lexer
from compiler.p4rser import Parser

# Add your parser tests here!


@pytest.mark.parametrize("test_program", ["example1.c"])
def test_parse_complete(test_program):
    lexer = Lexer()
    lexems = lexer.lex_file("examples/" + test_program)
    print(lexems)
    parser = Parser(lexems)
    parser.parse()
