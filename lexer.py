import ply.lex as lex

# Définition des tokens
tokens = [
    'NAME',
    'DATE',
    'RELATION',
    'ARROW',
    'LPAREN',
    'RPAREN',
    'COLON',
    'CONJUGATE',
]

# Expressions régulières pour les tokens
t_NAME = r'[a-zA-Z0-9]+'
t_DATE = r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}'
t_RELATION = r'père|mère'
t_ARROW = r'->'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
# t_CONJUGATE = r'est le conjoint de'
t_CONJUGATE=r'- CONJOINT ->'

# Ignorer les espaces et les tabulations
t_ignore = ' \t'

# Fonction pour gérer les erreurs de lexing
def t_error(t):
    print("Caractère illégal : '%s'" % t.value[0])
    t.lexer.skip(1)

# Création de l'objet lexer
lexer = lex.lex()

# Exemple d'utilisation du lexer
data = '''
Jean (01/01/1900-01/01/1980)
Marie (01/01/1910-01/01/1990)
père: Jean -> Marie
Marie est le conjoint de Jean
'''
lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
