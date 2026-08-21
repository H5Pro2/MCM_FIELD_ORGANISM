# S1-PS: Statischer Vertrag fuer eine kompatible schlanke Paketinitialisierung

## Status und Umfang

S1-PS bindet ausschliesslich den Migrationsvertrag fuer die spaetere
Paketinitialisierung. Es veraendert `mcm_field_organism/__init__.py` nicht,
erzeugt noch kein Exportmanifest und fuehrt keine Imports, Tests, Browser,
Sensoren oder Feldlaeufe aus. Es wird keine Datei geloescht und keine
Kandidatenmechanik geoeffnet.

Entscheidung:

```text
STATIC_LAZY_ROOT_MIGRATION_CONTRACT_BOUND_EXPORT_MAP_REQUIRED_NO_IMPLEMENTATION
```

## Ausgangslage

S1-PR trennt die beiden Oberflaechen:

```text
mcm_field_organism.current_api
    kuratierter aktiver Feldkern und explizite Referenzmanifeste

mcm_field_organism.__init__
    breite historische Kompatibilitaetsoberflaeche
```

Die `current_api`-Namensgrenze ist sauber. Beim Import eines Untermoduls
initialisiert Python jedoch zuerst das Paket. Die heutige Root-Datei importiert
deshalb bereits beim Paketstart eine grosse Zahl aktiver, historischer,
geschlossener und inaktiver Module.

Eine statische Suche findet 348 direkte Root-Importfundstellen in Tests und
Werkzeugen. Mehrere bestehende Grenztests verlangen ausserdem exakte
Objektidentitaet zwischen Root-Reexport und Ursprungsmodul. Eine Entfernung
der Root-Namen oder ein sofortiges Umschreiben aller Nutzer ist daher keine
kompatible Konsolidierung.

## Zielzustand

Der spaetere Zielzustand lautet:

```text
import mcm_field_organism.current_api
-> minimale Paketinitialisierung
-> Laden nur der von current_api benoetigten aktiven und expliziten
   Referenzmodule
-> kein eager Laden geschlossener Kandidaten, historischer Runner oder
   inaktiver Sensorpfade
```

Gleichzeitig muss weiterhin gelten:

```text
from mcm_field_organism import ExistingName
-> derselbe Gegenstand wie aus seinem bisherigen Ursprungsmodul
```

## Gebundene Migrationsform

Die einzig zugelassene Implementierungsform fuer die spaetere Migration ist
eine statische, vollstaendige Lazy-Exportabbildung:

```text
exportierter Root-Name
-> genau ein relatives Ursprungsmodul
-> genau ein Attributname
-> operative S1-PR-Klasse
```

Die Root-Datei darf spaeter nur noch laden:

- die unveraenderliche Exportabbildung;
- ein kleines Aufloesungsverfahren auf Basis der Standardbibliothek;
- die fuer Modulmetadaten erforderlichen Konstanten.

Die konkrete Aufloesung darf erst im Implementierungsschritt erfolgen. Als
technische Form ist ein modulares `__getattr__` mit `importlib` zulaessig.
Nach erfolgreicher Aufloesung muss das Objekt unter seinem Root-Namen gecacht
werden, sodass wiederholter Zugriff und direkter Modulimport dasselbe Objekt
liefern.

## Kompatibilitaetsinvarianten

Eine spaetere Implementierung wird nur akzeptiert, wenn alle folgenden
Invarianten gemeinsam gelten:

1. **Namensbestand:** Kein heutiger Name aus Root-`__all__` wird entfernt,
   umbenannt oder stillschweigend einer anderen Bedeutung zugeordnet.
2. **Reihenfolge:** Die kanonische `__all__`-Liste bleibt in Inhalt und
   Reihenfolge identisch, sofern ein spaeterer statischer Audit keine bereits
   vorhandene Dublette nachweist und separat sperrt.
3. **Objektidentitaet:** Root-Zugriff und direkter Ursprungsimport liefern
   fuer Klassen, Funktionen, Enums und Konstanten dasselbe Python-Objekt.
4. **Modulidentitaet:** `__module__`, Signaturen, Dataclassfelder und
   Exceptionklassen bleiben unveraendert.
5. **Fehlende Namen:** Ein nicht registrierter Root-Name erzeugt weiterhin
   `AttributeError`; es gibt keine heuristische Modulsuche.
6. **Explizite Submodule:** `from mcm_field_organism import current_api` und
   direkte Fachmodulimporte bleiben zulaessig.
7. **Sternimport:** `from mcm_field_organism import *` folgt weiterhin
   `__all__`. Dass dieser ausdruecklich breite Zugriff alle dort genannten
   Module laden kann, ist kompatibel und kein Aktivkernpfad.
8. **Introspektion:** Ein spaeteres `__dir__` muss statische Root-Namen und
   bereits geladene Modulattribute ohne Modulimport sichtbar machen.
9. **Caching:** Erfolgreich aufgeloeste Namen werden einmalig im
   Root-Modulnamespace gebunden; die Abbildung selbst wird nicht dynamisch
   veraendert.
10. **Keine Ausfuehrung:** Die Lazy-Aufloesung importiert nur das angegebene
    Modul und liest das angegebene Attribut. Sie startet keinen Runner,
    Browser, Sensor oder Feldschritt.

## Absichtlich geaenderte Fehlerzeit

Eine schlanke Initialisierung kann die heutige Fehlerzeit optionaler oder
historischer Module nicht unveraendert lassen. Deshalb wird genau folgende
Verhaltensaenderung vorab zugelassen:

```text
heute:
    Fehler eines eager importierten historischen Moduls kann bereits beim
    Paketimport auftreten

spaeter:
    derselbe Fehler darf erst beim ausdruecklichen Zugriff auf dessen
    Root-Namen oder beim direkten Import dieses Moduls auftreten
```

Nicht zugelassen sind:

- Unterdruecken oder Ersetzen des urspruenglichen Fehlers;
- Rueckgabe eines Platzhalters;
- automatisches Nachinstallieren einer Abhaengigkeit;
- Umleitung auf eine andere Implementierung;
- Fehler beim Import des aktiven Kerns aufgrund eines nicht angeforderten
  historischen, geschlossenen oder inaktiven Moduls.

## Exportabbildung und Klassifikation

Jeder Name muss vor der Implementierung genau eine S1-PR-Klasse tragen:

```text
ACTIVE_FIELD_CORE
REFERENCE_BASELINE
CLOSED_CANDIDATE
HISTORICAL_RUNNER
INACTIVE_SENSOR
```

Die Klasse steuert keine Runtime. Sie ist statische Provenienz und dient
nur dem Audit. Die Zuordnung muss aus der heutigen Root-Datei und den
verbindlichen Abschlussdokumenten erzeugt werden. Ein Default darf nur
`HISTORICAL_RUNNER` sein; aktive oder Referenzrollen duerfen niemals durch
Namensmuster geraten werden.

Pflichtfelder jedes spaeteren Records:

```text
export_name
source_module
source_attribute
surface_class
```

Die sortierte kanonische Recordmenge, die kanonische `__all__`-Liste und die
Quellfassung von `__init__.py` erhalten getrennte SHA-256-Digests. Dadurch
kann eine spaetere Codeaenderung nur gegen den vorregistrierten Bestand
erfolgen.

## Statische Stopplinien

Die Migration wird vor jeder Codeaenderung gestoppt, wenn der Exportaudit:

- einen Root-Namen keinem eindeutigen Ursprungsattribut zuordnen kann;
- denselben Namen mit verschiedenen Ursprungsobjekten findet;
- dynamisch erzeugte Root-Namen ausserhalb der statischen Abbildung findet;
- eine aktive Rolle nur ueber ein geschlossenes oder inaktives Modul
  aufloesen kann;
- einen Importzyklus findet, der durch Lazy-Aufloesung seine Objektidentitaet
  verlieren wuerde;
- fuer einen bestehenden Namen keine kompatible Fehlersemantik definieren
  kann.

Bei einem Stopp bleibt die heutige Root-Datei unveraendert.

## Spaeteres endliches Abnahmegate

S1-PS fuehrt dieses Gate noch nicht aus. Eine spaetere Implementierung muss
vorab ein endliches Testbudget binden und mindestens pruefen:

1. statische Vollstaendigkeit und Eindeutigkeit der Exportabbildung;
2. identischen `__all__`-Inhalt und identische Reihenfolge;
3. Objektidentitaet aller registrierten Root-Namen mit ihrem
   Ursprungsattribut;
4. `AttributeError` fuer nicht registrierte Namen;
5. korrekte `dir()`-Sicht ohne eager Modulimport;
6. Caching und wiederholte Identitaet;
7. Import des aktiven Feldkerns in einem frischen Unterprozess;
8. Abwesenheit geschlossener, historischer und inaktiver Modulgruppen in
   `sys.modules` unmittelbar nach diesem Aktivkernimport;
9. bestehende `current_api`-, Identitaets- und Architekturgrenztests;
10. ausdruecklichen breiten Root- und Sternimport als getrennten
    Kompatibilitaetsarm.

Der Unterprozess ist erforderlich, weil bereits geladene Module im
Testprozess eine Lazy-Isolationspruefung unbrauchbar machen wuerden.

## Aussage- und Projektgrenze

S1-PS ist reine technische Architekturpflege. Der Vertrag veraendert keine
Feldfunktion und liefert keine neue Substratprognose. Geschlossene Zweige
bleiben geschlossen; die Forschungspause bleibt bestehen.

## Genau ein naechster Schritt

```text
S1-PT - statischer Root-Exportinventar- und Eindeutigkeitsaudit
```

S1-PT soll `__init__.py` ausschliesslich statisch auswerten, jeden heutigen
Root-Namen seinem Ursprungsmodul und seiner S1-PR-Klasse zuordnen, Dubletten
oder Mehrdeutigkeiten fail-closed melden und die drei vorgesehenen Digests
binden. Noch keine Lazy-Implementierung, keine Aenderung an `__init__.py` und
keine Testausfuehrung.
