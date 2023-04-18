import textwrap

# Liste des événements
events = [
    ('20/07/1969', 'Premier pas sur la Lune'),
    ('04/09/1998', 'Création de Google'),
    ('09/01/2007', 'Présentation de l\'iPhone'),
    ('26/03/2019', 'Première image d\'un trou noir'),
]

# Longueur de la frise chronologique
timeline_length = 50

# Détermine la date du premier événement
first_event_date = min([event[0] for event in events])

# Crée la frise chronologique
timeline = ''
for event in events:
    # Détermine la position de l'événement sur la frise
    event_date = event[0]
    event_position = int((int(event_date[:4]) - int(first_event_date[:4])) / 10 * timeline_length)

    # Ajoute l'événement à la frise
    event_description = event[1]
    wrapped_description = textwrap.wrap(event_description, width=30)
    timeline += '{: <{}}| {}\n'.format('', event_position, event[0])
    for line in wrapped_description:
        timeline += '{: <{}}| {}\n'.format('', event_position, line)

# Affiche la frise chronologique
print(timeline)
