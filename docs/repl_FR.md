### `replkit.generic_repl` — REPL générique personnalisable

**Un moteur REPL extensible avec prise en charge de l'historique, de la complétion, des alias, et des fichiers d'initialisation.**

---

## Classe `GenericREPL`

### Constructeur

```python
GenericREPL(
    interpreter,
    history_file=".repl_history",
    history_length=1000,
    aliases_file=".repl_aliases",
    hello_sentence="Welcome to the REPL!",
    prompt=">>> ",
    logger=None
)
```

### Attributs principaux

- `interpreter`: Instance dotée de `.eval()` et éventuellement `.get_keywords()`
- `history_file`: Fichier d’historique pour `readline`
- `aliases_file`: Fichier contenant les définitions `.alias`
- `prompt`: Prompt affiché
- `logger`: Logger Python configuré

---

## Fonctions clés

### `loop()`

Démarre la boucle REPL interactive.

### `expand_aliases(line)`

Déploie les alias dans la ligne (par ex. `@foo` devient son expression). Soulève une `ValueError` si l’alias est inconnu.

### `handle_alias_command(line)`

Gère `.alias`, `.unalias` et leur affichage. Renvoie `True` si c’était une commande interne, `False` sinon.

### `load_file(path, label=None, show_errors=True)`

Exécute les lignes d’un fichier (interprète ou traite les alias).

### `print_history()`, `init_history()`, `save_history()`

Gère l’historique utilisateur.

### `load_aliases_file(path)`, `save_aliases_file(path)`

Charge ou sauvegarde les alias vers un fichier.

---

## Autres classes

### `REPLCompleter`

Complétion pour `readline` incluant :

- mots-clés de l’interpréteur
- commandes `.alias`, `.exit`, etc.
- noms d’alias définis
- historique utilisateur

---

## Point d’entrée CLI : `repl()`

```bash
python generic_repl.py --history ~/.hist --alias ~/.aliases --log repl.log
```

### Options supportées

| Option       | Description                       |
| ------------ | --------------------------------- |
| `--history`  | Fichier d’historique              |
| `--alias`    | Fichier d’alias `.alias ...`      |
| `--log`      | Fichier de log                    |
| `--loglevel` | Niveau de log (DEBUG, INFO, etc.) |
| `--hello`    | Message de bienvenue              |
| `--prompt`   | Texte du prompt                   |
| `--run`      | Une ligne de commande à exécuter  |
| `--file`     | Fichier à exécuter à l’ouverture  |

---

## Aliases (`@name`)

- `@` obligatoire (ex: `@double = dup +`)
- Pré-substitution automatique avant `eval()`
- Sécurité : noms valides uniquement, erreurs claires
- Complétion disponible
- Sauvegarde/restauration via fichier `.alias`

---

## Exemple minimal

```python
from replkit.generic_repl import repl

class MyInterpreter:
    def eval(self, line):
        print(f"Eval: {line}")
    def get_keywords(self):
        return {"print", "run", "exit"}

repl(MyInterpreter())
```
