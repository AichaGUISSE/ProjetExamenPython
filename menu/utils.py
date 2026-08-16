"""Petites fonctions de saisie réutilisées dans les menus."""


def demander_choix_parmi(prompt, options):
    """Affiche une liste numérotée et renvoie la VALEUR INTERNE choisie.

    `options` est une liste de tuples (valeur_interne, libellé_affiché),
    par exemple [("ADMIN", "Admin"), ("TECHNICIEN", "Technicien")].
    """
    while True:
        print(prompt)
        for index, (valeur, libelle) in enumerate(options, start=1):
            print(f"{index}. {libelle}")

        saisie = input("Choix : ").strip()

        if not saisie.isdigit():
            print("Merci d'entrer un numéro valide.\n")
            continue

        index_choisi = int(saisie)
        if not (1 <= index_choisi <= len(options)):
            print("Numéro hors liste.\n")
            continue

        return options[index_choisi - 1][0]


def demander_non_vide(prompt):
    while True:
        valeur = input(prompt).strip()
        if valeur:
            return valeur
        print("Ce champ est obligatoire.\n")


def demander_entier(prompt):
    while True:
        saisie = input(prompt).strip()
        if saisie.isdigit():
            return int(saisie)
        print("Merci d'entrer un nombre entier valide.\n")


def demander_email(prompt):
    while True:
        valeur = input(prompt).strip()
        domaine = valeur.split("@")[-1] if "@" in valeur else ""
        if valeur.count("@") == 1 and "." in domaine and len(domaine) > 2:
            return valeur
        print("Adresse email invalide (format attendu : nom@domaine.ext).\n")