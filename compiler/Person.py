from datetime import datetime

def format_str_date(date):
    # receive a date in datetime format and return a string
    # Condition to check if the date is not None
    if date is None:
        return ""
    else:
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
        self.gen = None
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
        """
        Retourne le nom des parents ordonnés par ordre alphabétique
        :return:
        """
        if len(self.parents) >= 2:
            if self.parents[0].name < self.parents[1].name:
                return [self.parents[0].name, self.parents[1].name]
            else:
                return [self.parents[1].name, self.parents[0].name]
        else:
            return [self.parents[0].name]


    def get_couple_names(self):
        """
        Retourne le nom des mariés du couple ordonnés par ordre alphabétique
        :return:
        """
        if self.name < self.spouse.name:
            return str(self.name + self.spouse.name)
        else:
            return str(self.spouse.name + self.name)

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



