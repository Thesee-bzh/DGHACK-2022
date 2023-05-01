# Dev / ASMère

## Challenge
Nous avons besoin de sécuriser des données sur un très vieux système.

Heureusement, nous avons déjà de nombreux programmes très sophistiqués pour le faire.

Nous avons cependant égaré l'interpreteur du langage de programmation interne à notre organisation.

Veuillez programmer l'interpreteur ASMera en Python, suivant les entrées et sorties d'exemple ci-dessous.

Le programme prend pour seul argument le fichier à interpreter et affiche le résultat en sortie standard.

Le test final peut contenir des opérations == != < > <= ainsi que >=

## Inputs
- [example_input.txt](./example_input.txt)
- [example_output.txt](./example_output.txt)
- [example_incrementer_input.txt](./example_incrementer_input.txt)
- [example_incrementer_output.txt](./example_incrementer_output.txt)

## Solution
We need to parse following syntax elements, as given in example files:
- function declaration, like `fonction_simple: (...)`
- function call, like `fonction_simple()`
- integer variable assignment, like `nombre nombre_entier -10`
- integer variable increment, like `incrementer nombre_exemple 5`
- integer variable evaluation, like $nombre_exemple
- output to stdout, including quoted strings, unquoted strings and variable evaluation, like `message "oh mais si si... " "je peux afficher " $nombre_entier`
- condition evaluation, like: `si $nombre_exemple < 10`

The way I took it is to dynamically generate the corresponding Python program, then dynamically execute it using Python's `exec()` call.

Let's walk through a simple test program, similar to the example one:
```
fonction_inutile:
message non affiché
retour

message ici un texte sans variable ni guillemets
nombre nombre_entier -10
appel fonction_inutile
```

A dynamically generated Python-equivalent program will look like so, and stored in variable `prog`:
```python
p = """
def fonction_inutile():
        print("non affiché", sep='')

print("ici un texte sans variable ni guillemets", sep='')
global nombre_entier
nombre_entier = -10
fonction_inutile()
"""
exec(p)
```

Then calling `exec(prog)` will effectively execute the generated Python program, producing the expected output:
```
ici un texte sans variable ni guillemets
non affiché
```

Here is the generated Python program for the complete `example_input.txt`:
```python
p = """
def fonction_inutile():
        print("non affiché", sep='')

def affiche_nombre():
        global nombre_exemple
        nombre_exemple = 0
        nombre_exemple += 5
        print("on affiche ", nombre_exemple," dans la console", sep='')
        fonction_recursive()

def messages_complexes():
        print(" ", sep='')
        print("ce message doit avoir des espaces normaux", sep='')
        print("ce message doit avoir des espaces normaux aussi", sep='')
        print("tandis que ce texte, qui affiche ", nombre_exemple," n'aura que des espaces uniques", sep='')
        print("", nombre_exemple,"  peut etre affiché : ", nombre_exemple," et affiché de nouveau : ", nombre_entier," et voilà !", sep='')
        print("cependant, entre des doubles guillemets, $nombre_exemple s'affiche '$nombre_exemple'", sep='')
        print("ici  on  obtient  deux  espaces  entre  chaque  mot", sep='')
        print("oh mais si si... je peux afficher ", nombre_entier,"", sep='')

def fonction_recursive():
        global nombre_exemple
        if(nombre_exemple<10):
                nombre_exemple += 1
                global nombre_entier
                nombre_entier += -10
                print("le nombre est ", nombre_exemple,"", sep='')
                fonction_recursive()


def fonction_simple():
        print("bonjour", sep='')
        affiche_nombre()

print("ici un texte sans variable ni guillemets", sep='')
global nombre_entier
nombre_entier = -10
fonction_simple()
print("test", sep='')
messages_complexes()
"""
exec(p)
```

Storing this into variable `prog` then calling `exec(prog)` effectively produces the same output as in `example_output.txt`.

Now the parsing of the input is done one line after each other. The correspondance with Python syntax is pretty straightforward, except the following:
- Handling of indentation, which is absolutely essential in Python
- Handling of globals: I handle a list of global variables encountered when parsing the input. A `global` statement is added inside of a function, when a global variable needs to be evaluated (if not already)
- Message parsing: parsing messages with quoted strings, unquoted strings and variables was a headache, resulting in a dirty peace of code...

Full code is provided below.

## Python code
Complete solution in [ASMera.py](./ASMera.py)

## Flag
No flag, challenge is completed after code submission
