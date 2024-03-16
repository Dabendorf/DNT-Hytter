# DNT Hytter Oversikt
Dette lille skriptet her melker informasjoner om DNT sine hytter fra ut.no og konverter den til både tabell, kart og gpx-fil (for import i kartapps). Programmet forutsetter at APIen til ut.no ikke har forandret seg siden dagen dette her ble skrevet (2024-03-16)

## Teknisk oversikt
Scripten er skrevet i Python 3.11. Nødvendige pakker som trengs for å bruke den kan installeres via ``requirements.txt``

```pip3 install -r requirements.txt```

### Scripter
Programmet finnes både som jupyter notebook for egen utforskning og som python-fil som kun genererer dataen man trenger.

### Output
Programmet genererer midlertidige json-filer som ble hentet fra ut.no sin API samt de følgende output-filene

* fd
* fsd