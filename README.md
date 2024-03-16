# DNT Hytter Oversikt
Dette lille skriptet her melker informasjoner om DNT sine hytter fra ut.no og konverter den til både tabell, kart og gpx-fil (for import i kartapps). Programmet forutsetter at APIen til ut.no ikke har forandret seg siden dagen dette her ble skrevet (2024-03-16)

## Teknisk oversikt
Scripten er skrevet i Python 3.11. Nødvendige pakker som trengs for å bruke den kan installeres via ``requirements.txt``

```pip3 install -r requirements.txt```

### Scripter
Programmet finnes både som jupyter notebook for egen utforskning og som python-fil som kun genererer dataen man trenger.

### Henting av data
Oppe finnes det en variable med navn ``fetch_data_from_api_again``. Hvis den er satt på ``True``, så hentes dataen på nytt. Om du velger å leke med koden, sett verdien på ``False``, så dataen ikke må hentes på nytt hele tiden. Tenk på pengvinene!

### Output
Programmet genererer midlertidige json-filer som ble hentet fra ut.no sin API samt de følgende output-filene

* ``alle_hytter.csv``: Liste med alle hytter og diverse egenskaper
* ``map_norway.html``: Interaktivt kart over alle hytter i Norge
* ``map_vestlandet.html``: Interaktivt kart over alle hytter på Vestlandet
* ``points.gpx``: gpx fil for å importere alle hytter i en app som for eksempel Organic Maps
