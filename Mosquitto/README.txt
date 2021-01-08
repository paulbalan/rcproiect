Pentru utilizarea mosquitto:

1) Se ia de pe mosquitto.org varianta pentru windows x64 
2) Se da replace la fisierul mosquitto.conf din folderul instalarii 
3) Se deschide consola la locatia instalarii mosquitto si se ruleaza comanda
		mosquitto -c mosquitto.conf
4) Acum serverul de mosquitto este pornit si se poate testa programul


Pentru a seta logarea cu username si parola:
1)In directorul unde este instalat Mosquitto se face un fisier txt in care se vor memora parolele, ex: passwd.txt
2)In acest fisier se scriu conturile cate unul pe linie in formatul username:parola
3)Cu un terminal deschis in directorul cu mosquitto se apeleaza comanda: mosquitto_passwd -U passwd pentru a cripta parola, 
unde passwd e numele fisierului cu parole

ATENTIE!
Comanda cripteaza tot ce gaseste acolo, astfel ca daca deja exista o parola criptata, o va mai cripta odata si acel cont nu 
va mai putea fi utilizat

4)In directorul unde este instalat Mosquitto se deschide fisierul mosquitto.conf
5)Se cauta linia cu allow_anonymous si se inclocuieste cu: allow_anonymous false
6)Se cauta linia cu password_file si se scrie calea catre fisierul cu parole, exemplu: C:\Program Files\mosquitto2\passwd.txt
7)Se salveaza, reseteaza Mosquitto, personal a trebuit sa resetez si calculatorul