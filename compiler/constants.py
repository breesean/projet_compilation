LEXEM_REGEXES = [
    # Comments and whitespaces
    (r"\/\/.*", "COMMENT"),
    (r"[ \t\n]+", None),
    # Links
    (r'family_tree',"KW_TREE"),
    (r'<=>', "MARITAL_LINK"),
    (r'->', "FAMILIAL_LINK"),
    # Special characters
    (r"\(", "L_PAREN"),
    (r"\)", "R_PAREN"),
    (r"\{", "L_CURL_BRACKET"),
    (r"\}", "R_CURL_BRACKET"),
    (r'\;', 'TERMINATOR'),
    (r'\-', 'RANGE'),


    #Others
    (r'\d{1,2}\/\d{1,2}\/\d{4}', "DATE"),
    (r'[a-zA-Z]+', "NAME"),

]
