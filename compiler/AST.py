import graphviz as gv

# Définition de la classe AST

def format_str_date(date):
    # receive a date in datetime format and return a string
    # Condition to check if the date is not None
    if date is None:
        return ""
    else:
        return date.strftime("%d/%m/%Y")

class AST:
    def __init__(self):
        self.graph = gv.Digraph(format='svg')
        # Ajout du noeud "family_tree"
        self.graph.node('family_tree_AST', label='family_tree_AST')

    def def_declaration(self,name,bdate,ddate=None, racine=False):
        # Si la date de décès est inconnue, on ne l'affiche pas
        if ddate == None:
            label = name + '\n' + bdate
        else:
            label = name + '\n' + bdate + '-' + ddate
        # Ajout du noeud (on prend le nom + la date de naissance comme identifiant pour avoir une clef unique)
        self.graph.node(name + bdate, label=label, shape='box')

        # Condition si la déclaration concerne la racine de l'arbre
        if racine:
            # Ajout de l'arête entre le noeud et l'origine de l'AST
            self.graph.edge('family_tree_AST', name+bdate, label='racine')
        else:
            # Ajout de l'arête entre le noeud et l'origine de l'AST
            self.graph.edge('family_tree_AST', name+bdate, label='declaration')

    def def_marital_link(self, name1, bdate1, name2, bdate2, wedding_date=None):
        # Ajout du noeud mariage et de l'arête depuis l'origine de l'AST
        if wedding_date == None:
            wedding_node = 'marriage' + name1 + name2
            label_wedding_node = '♥ Mariage ♥'
        else:
            wedding_node = 'marriage' + name1 + name2 + wedding_date
            label_wedding_node = '♥ Mariage ♥\n' + wedding_date
        self.graph.node(wedding_node, label=label_wedding_node, shape='diamond')
        self.graph.edge('family_tree_AST', wedding_node)

        # Ajout des deux noeuds des personnes + arête depuis le noeud de mariage
        label1 = 'wedd' + name1 + format_str_date(bdate1)
        label2 = 'wedd' + name2 + format_str_date(bdate2)
        self.graph.node(label1, label=name1 + '\n' + format_str_date(bdate1), shape='box')
        self.graph.node(label2, label=name2 + '\n' + format_str_date(bdate2), shape='box')
        self.graph.edge(wedding_node, label1)
        self.graph.edge(wedding_node, label2)

    def def_familial_link(self, parent, bdate_parent, child, bdate_child):
        # Ajout du noeud de lien familial et de l'arête depuis l'origine de l'AST
        label_familial_node = 'familial' + parent + child
        self.graph.node(label_familial_node, label='familial_link')
        self.graph.edge('family_tree_AST', label_familial_node, label='familial_link')

        # Ajout des deux noeuds des personnes + arête depuis le noeud de lien familial
        label1 = 'fam' + parent + bdate_parent
        label2 = 'fam' + child + bdate_child
        self.graph.node(label1, label=parent + '\n' + bdate_parent, shape='box')
        self.graph.node(label2, label=child + '\n' + bdate_child, shape='box')
        self.graph.edge(label_familial_node, label1)
        self.graph.edge(label_familial_node, label2)


    def show_AST(self):
        self.graph.render('test-output/round-table.gv', view=True)
"""
a = AST()
a.def_declaration('Jean','01/01/2000',racine=True)
a.def_declaration('Marie','01/01/2000',racine=False,ddate='01/01/2100')
a.def_marital_link('Jean','01/01/2000','Marie','01/01/2000')
a.def_declaration('Pierre','01/01/2000',racine=False,ddate='01/01/2100')
a.def_familial_link('Jean','01/01/2000','Pierre','01/01/2000')

a.show_AST()
"""