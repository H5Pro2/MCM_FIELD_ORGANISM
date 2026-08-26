# S1-QD: Statischer Zustands-, Handoff- und Ausgabevertrag fuer das Pflichtbaselinepaket

## Status und Umfang

S1-QD bindet die kleinsten privaten Zustandsrollen, Frischstartgrenzen,
Carryregeln, Eingabegrenzen und atomaren Ausgaben fuer die in S1-QC
festgelegten Adaptergruppen A0 bis A3 und Abschlussrollen M1 bis M5.

Der Vertrag enthaelt:

- keine Updategleichung oder Ausgabegleichung;
- keine Parameter, Werte, Dimensionen, Dauern oder Toleranzen;
- keine konkrete Schema-ID, Konfigurationsdatei, Fixture oder Digest;
- keine Adapter- oder Baselineimplementierung;
- keine Runtimeaenderung, keinen Test und keinen Feldlauf;
- keine Kandidatenauswahl und keine Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
ROLE_SPECIFIC_PRIVATE_STATE_OWNERSHIP_AND_FRESH_CARRY_BOUND
MODEL_NEUTRAL_INPUT_AND_ATOMIC_COMPLETE_OUTPUT_BOUND
A0_AND_A3_FIELD_HANDOFF_ADMISSIBILITY_REMAINS_OPEN
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gemeinsame Schichten

Eine spaetere Baselinehuelle muss vier voneinander getrennte Schichten
besitzen:

| Schicht | Aufgabe | Verbotene Information |
|---|---|---|
| `ORCHESTRATION` | Familie, Arm, Ereignisrolle, Ordinal und Checkpoint verwalten | keine direkte Modellwirkung |
| `MODEL_INPUT` | Feld, Rezeptorkontakt, Geometrie und abgeschlossenes Zeitintervall uebergeben | Arm-, Ziel-, Ergebnis- oder Zukunftswissen |
| `PRIVATE_STATE` | genau den eigenen vollstaendigen Modellzustand tragen | Kandidatenzustand und Zustand anderer Baselines |
| `OBSERVATION_OUTPUT` | komplettes Feld, privaten Zustandsbeleg und Diagnostik atomar ausgeben | keine Nachberechnung oder Reparatur |

Familien- und Armnamen bleiben ausschliesslich in `ORCHESTRATION`. Eine
Baseline sieht nur die wertidentische technische Geschichte, nicht deren
beabsichtigte Forschungsrolle.

## Gemeinsame modellneutrale Eingabehuelle

Jeder ausfuehrbare Feldarm A0 bis A3 sowie M1, M2, M4 und M5 muss spaeter pro
abgeschlossenem Intervall genau eine unveraenderliche Eingabehuelle erhalten.
Sie bindet mindestens:

- Modellrollen- und Vertragsidentitaet;
- unveraenderte Konfigurationsidentitaet;
- Geometrieidentitaet und kanonische Knotenreihenfolge;
- vollstaendigen vorherigen gemeinsamen Feldzustand;
- aktuellen Rezeptor- und Kontaktinput;
- Anfang und Ende des technischen Intervalls;
- vollstaendigen vorherigen privaten Modellzustand oder eine ausdrueckliche
  Zustandslosmarkierung;
- Eingabe- und Vorzustandsprovenienz;
- atomaren Validierungsstatus.

Nicht Bestandteil der Modelleingabe sind:

- Expositionsfamilie, Armname oder erwartete Kontrastrichtung;
- Checkpoint-, Probe-, Gap-, Bildungs- oder Freigabelabel;
- Kandidatenzustand, Kandidatenbilanz oder Kandidatenkapazitaet;
- Comparatorstatus, Zielvektor oder Referenzergebnis;
- spaetere Eingaben, spaetere Zustaende oder Laufresultate;
- Retry-, Fit-, Reparatur- oder Optimierungsanweisungen.

Die Begriffe aus S1-PZ bleiben Orchestrierungsrollen. Ein Gap ist fuer ein
Modell nur ein normales Intervall mit dem registrierten Nullkontaktinput.

## Frischstart und Carry

Jeder Arm wird unabhaengig aus derselben registrierten Quelle aufgebaut. Der
Frischstart besteht aus:

1. einem digestgleichen gemeinsamen Frischfeld;
2. einer zur Modellrolle gehoerenden privaten Frischzustandsfabrik;
3. genau einer unveraenderten Konfigurationsidentitaet;
4. einer frischen Provenienzkette ohne Vorgeschichte eines anderen Arms.

Ein Frischzustand darf nicht durch Nullsetzen eines gebrauchten Zustands
erzeugt werden. Der naechste Zustand eines Intervalls wird im selben Arm
bitgenau als Vorzustand des folgenden Intervalls getragen. Kein anderer Arm,
kein anderes Modell und kein spaeterer Replikatlauf darf diesen Zustand
uebernehmen.

Ein Carry ist nur gueltig, wenn Modellrolle, Geometrie, Knotenordnung,
Konfiguration und Zustandsdigest lueckenlos zusammenpassen. Bei einer
Abweichung wird kein Teilzustand uebernommen.

## Angleichung und passive Beobachtung

`ALIGN_READOUT_SH` darf ausschliesslich den aktuellen gemeinsamen
Rezeptorkontakt sowie S und H auf die registrierte Vergleichslage abbilden.
Dabei gilt:

- keine Feldzeit vergeht;
- keine Baseline wird aufgerufen;
- kein privater Zustand wird gelesen, fortgeschrieben oder ersetzt;
- die vollstaendige private Zustandsserialisierung bleibt bitgleich;
- die Angleichungsprovenienz wird ausserhalb des Modells gebunden.

`OBSERVE` liest erst nach einem atomar abgeschlossenen Intervall oder einer
abgeschlossenen Probe. Es gibt keinen Observercallback innerhalb einer
Baselinegleichung.

## Gemeinsame atomare Ausgabehuelle

Jeder ausfuehrbare Feldarm muss pro Intervall atomar liefern:

- Modellrolle, Vertrags- und Konfigurationsidentitaet;
- Eingabe-, Vorzustands- und Geometrieprovenienz;
- vollstaendigen naechsten gemeinsamen Feldzustand;
- vollstaendigen naechsten privaten Zustand oder Zustandslosmarkierung;
- kanonischen privaten Zustandsdigest;
- vollstaendige technische Diagnostik getrennt vom Feldreadout;
- Eigendigest der gesamten Ausgabe;
- genau einen Abschlussstatus.

Nach einer Probe muss das spaetere Resultatbuendel zusaetzlich die
vollstaendige vorzeichenbehaftete S-Fortsetzung in kanonischer
Komponentenreihenfolge tragen. Private Baselinerohozustaende duerfen nicht als
Kandidatenbilanz oder Feldreadout umgedeutet werden.

Ist ein Bestandteil ungueltig oder fehlt er, wird weder Feld noch privater
Folgezustand veroeffentlicht. Diagnostik allein ist kein Teilergebnis.

## A0 - Zustandsloser aktueller Kontakt

### Privater Zustand

A0 besitzt keinen privaten Zustand. Die Huelle traegt nur eine kanonische
Zustandslosmarkierung. Ein leerer, aber veraenderlicher Container ist nicht
zulaessig.

### Frischstart und Carry

A0 erzeugt bei jedem Frischstart dieselbe Zustandslosmarkierung. A0 selbst
darf weder Kontaktpraefixe noch Zwischenoutputs speichern. Ob der gemeinsame
Feldzustand fuer A0 fortgefuehrt oder aus dem aktuellen Kontakt rein formal
gebildet werden darf, bleibt dem Handoff-Audit vorbehalten; keine Variante
darf A0 einen privaten Verlauf geben.

### Kernelhandoff

Der vorhandene Kern `carrier_baselines.stateless_baseline` darf nur den
aktuellen Kontakt und seinen ausdruecklich leeren Nachhall ausgeben. Der
noch fehlende Feldhandoff darf:

- Knoten nur nach der registrierten Geometrie anordnen;
- vorhandene Werte nur typ- und formgleich uebertragen;
- keinen Verlauf, Nachhall, Integrator oder Kopplungsterm einfuehren.

Ob ein solcher rein formaler Handoff mit dem bestehenden Feldkern moeglich
ist, bleibt offen. Benoetigt er eine neue Feldfortschreibung, ist A0 nicht als
unveraenderter Adapter anschliessbar.

### Ausgabe und Sperre

A0 muss spaeter ein vollstaendiges gemeinsames Feldresultat mit
Zustandslosbeleg liefern. Ein `CarrierFrame` allein ist kein zulaessiges
S1-QA-Resultat. Jede nichtleere private Zustandsprovenienz oder jeder
geschichteabhaengige Output sperrt A0.

## A1 - Kandidatenfreier schneller S/H-Feldkern

### Privater Zustand

A1 besitzt keinen zusaetzlichen Zustand ausserhalb des vollstaendigen
gemeinsamen S/H-Feldes. S und H sind Feldzustand und duerfen nicht als
verdeckter zweiter Baselinezustand dupliziert werden.

### Frischstart und Carry

A1 startet aus dem gemeinsamen Frischfeld und traegt das vollstaendige
Ergebnis von `advance_neutral_fast_shared_field` beziehungsweise dessen
transienter Variante durch jedes folgende Intervall. Die Auswahl der
Intervallform folgt ausschliesslich dem technischen Eingabetyp und nicht der
Expositionsrolle.

### Ausgabe und Sperre

Die Ausgabe ist das vollstaendige gemeinsame Feld plus ausdruecklicher Beleg,
dass kein weiterer privater Zustand existiert. Ein kandidatenbezogener
Substratzustand, eine armweise H-Konfiguration oder eine zweite H-Kopie
sperrt A1.

## A2 - Bestehende B1-B6-Feldintervallkerne

### Gemeinsame Grenze

A2 verwendet die vorhandene atomare Ausgabe aus vollstaendigem Feld,
`next_private_state`, Diagnostik und Ausgabedigest. Alte Profil- und Armhuellen
werden nicht uebernommen.

Die privaten Rollen bleiben getrennt:

| Rolle | Vollstaendiger privater Zustand |
|---|---|
| B1 | unveraenderter Fixed-Adapter-Payload samt Konfigurationsbezug |
| B2 | vollstaendiger lokaler L-Zustand in kanonischer Knotenordnung |
| B3 | vollstaendiger lokaler M-Zustand und sein Geometriebezug |
| B4 | vollstaendiger Zustand des linearen F3-Kerns |
| B5 | vollstaendiger Zustand des vollen F3-Kerns |
| B6 | vollstaendiger Zustand des CONST-V-Kerns samt eingefrorenem Spezifikationsbezug |

### Frischstart und Carry

Jede B-Rolle besitzt eine eigene registrierte Frischzustandsfabrik. Ein
B-Zustand darf niemals in eine andere B-Rolle konvertiert werden. Das
vollstaendige Feld und `next_private_state` eines gueltigen Outputs bilden
gemeinsam den naechsten Vorzustand.

### Ausgabe und Sperre

Ein A2-Output ist nur gueltig, wenn Feld, Privatstatus, Geometrie und
Konfigurationsidentitaet dieselbe Modellrolle tragen. Fehlender eingebetteter
Zustand, eine alte Profilkennung, ein Armparameter oder eine nachtraegliche
Anpassung sperrt den gesamten A2-Arm.

## A3 - Saettigung und Normalisierung

### Privater Zustand

Jede A3-Unterrolle traegt genau einen vollstaendigen lokalen latenten Zustand
pro registriertem Feldort. Saettigung und Normalisierung besitzen getrennte
Modell- und Konfigurationsidentitaeten und duerfen keinen Zustand teilen.

Der normalisierte Observeroutput ist kein zusaetzlicher Zustand. Eine global
berechnete Ausgabegroesse darf nicht verdeckt in den naechsten latenten
Zustand zurueckgeschrieben werden.

### Frischstart und Carry

Der vorhandene W7-N-Frischzustand wird fuer jede Unterrolle und jeden Arm
unabhaengig aufgebaut. Nur der vollstaendige latente Folgezustand wird
getragen. Der vorherige Observeroutput ist kein Eingabekanal.

### Feldhandoff und Sperre

`W7NLocalBaselineResult` liefert lokalen Zustand und Output, aber noch keine
vollstaendige Feldfortsetzung. Ein zulaessiger Handoff duerfte ausschliesslich
eine bereits vorhandene, unveraenderte Feldabbildung verwenden. Er darf keine
neue Rueckwirkung, Kopplung, Gewichtung oder zeitliche Dynamik definieren.

Solange diese Abbildung nicht nachgewiesen ist, bleibt A3
`FIELD_HANDOFF_UNBOUND`. Observeroutput allein darf nicht gegen eine
S1-QA-Feldfortsetzung verglichen werden.

## M1 - Feste Mehrzeitskalenbank

### Minimaler privater Zustand

M1 benoetigt eine endliche, kanonisch geordnete Menge unabhaengiger passiver
Spurkomponenten pro Feldort. Jede Komponente besitzt eine feste
Konfigurationsidentitaet. Komponenten duerfen weder miteinander interagieren
noch Arm- oder Ereignisrollen lesen.

Die konkrete Komponentenanzahl, Zeitkonfiguration, Initialwerte und
Ausgabeabbildung bleiben ungebunden. Eine nach einem Ergebnis ausgewaehlte
Teilmenge ist verboten.

### Frischstart, Carry und Ausgabe

Alle Komponenten werden gemeinsam aus einer registrierten Frischfabrik
erzeugt und als ein unteilbarer Zustand getragen. M1 muss spaeter sowohl den
kompletten Komponentenstatus als auch ein vollstaendiges gemeinsames
Feldresultat atomar liefern.

Fehlt eine Komponente, wechselt ihre Ordnung oder wird eine Komponente nur in
bestimmten Armen aktiviert, ist M1 ungueltig.

## M2 - Begrenzter Verlaufspuffer fuer Delay und Replay

### Minimaler privater Zustand

M2 besitzt einen endlichen, kanonisch geordneten privaten Puffer aus exakt den
modellneutralen Eingaberecords, die der Baseline bereits kausal vorlagen. Der
Zustand bindet:

- unveraenderte Modusidentitaet `DELAY` oder `REPLAY`;
- geordnete gespeicherte Eingaberecords;
- deren Geometrie-, Zeit- und Eingabedigests;
- Beleg der registrierten endlichen Puffergrenze;
- kanonische Auswahl- und Ausgabeposition.

Gespeichert werden duerfen keine Armnamen, Zielwerte, Ergebnislabels,
Kandidatenzustaende oder Observerresultate.

### Frischstart, Carry und Ausgabe

Der Frischpuffer ist leer und wird pro Arm unabhaengig erzeugt. Der gesamte
Pufferzustand wird atomar getragen; ein externes Dateisystem, globaler Cache
oder geteilter Replaybestand ist verboten.

M2 muss spaeter Pufferzustand, Auswahlprovenienz und vollstaendiges
Feldresultat gemeinsam ausgeben. Die konkrete Puffergrenze, Delayrolle,
Replayordnung und Feldabbildung bleiben fuer einen spaeteren Vertrag offen.

Zukunftszugriff, unbegrenztes Wachstum, nachtraegliche Auswahl oder ein
Pufferuebertrag zwischen Armen sperrt M2.

## M3 - Lokales Capacity-Clamp-Reduktionsgate

### Zustands- und Eingabegrenze

M3 ist kein Feldarm und besitzt keinen privaten Carryzustand. Es wird erst
passiv auf ein vollstaendiges, unveraenderliches Kandidaten-Beobachtungs- und
Bilanzrecord angewendet. Dieses Record muss die vom Kandidaten selbst vorab
deklarierten Angebots-, Freiheits- und Commitrollen bereits enthalten.

M3 darf keine fehlende Kandidatenvariable rekonstruieren, keinen
Kandidatenzustand parsen und keine Baseline- oder Feldgleichung aufrufen.

### Ausgabe und Sperre

M3 liefert nur einen Reduktionsbeleg mit Eingabedigest,
Vertragsidentitaet, Vollstaendigkeitsstatus und atomarem Gateausgang. Es
liefert kein Feld, keinen Folgezustand und keinen Kandidatenersatz.

Fehlt eine erforderliche oeffentliche Beobachtungsrolle, lautet der Ausgang
ausschliesslich `NOT_COMPUTABLE`. Ein aus Kandidatenprivatdaten gebauter
Clampzustand oder ein eigener Feldarm sperrt M3.

## M4 - Eingefrorene DTS-1/T1-Dreirollenbaseline

### Privater Zustand

M4 traegt den vollstaendigen eingefrorenen DTS-1-Dreirollenzustand pro
registrierter Kante zusammen mit seinem Geometrie- und Ressourcenledgerbezug.
Der T1-Kern bleibt eine strukturelle lokale Validierung derselben
`free/bound/blocked`-Anatomie und kein zweiter Feldzustand.

### Frischstart und Carry

M4 darf nur die bestehende registrierte DTS-1-Frischzustandsfabrik und den
unveraenderten geschlossenen Feldschritt verwenden. Das komplette Feld und
das komplette Dreirollenledger werden gemeinsam getragen. Historische
Recovery-on/off-Sidecars, alte Profilzustandsuebernahmen und G2/D3-Rollen
sind verboten.

### Ausgabe und Sperre

M4 muss vollstaendiges Feld, vollstaendiges Ledger, lokale
Erhaltungsvalidierung, Zustandsdigest und Diagnostik atomar liefern. Jede neue
Ressourcenrolle, geaenderte Rollenfolge, neue Recoveryregel oder
kandidatenspezifische Ausgabedeutung sperrt M4.

## M5 - Allgemeine Einzustandsretention

### Minimaler privater Zustand

M5 besitzt genau eine unabhaengige Retentionskoordinate pro registriertem
Feldort. Der Zustand bindet Modell-, Geometrie- und Konfigurationsidentitaet
und darf keine zweite Spur, kein Ledger, keinen Verlaufspuffer und keine
Armrolle enthalten.

Der vorhandene G2/D3-Zweischritt kann nur als strukturelle Referenz fuer
kanonischen Zustand und Fail-Closed-Ausgabe dienen. Seine Ereignisbindung,
Checkpointzahl und feste Konfiguration werden nicht in M5 uebernommen.

### Frischstart, Carry und Ausgabe

Alle lokalen Koordinaten werden gemeinsam aus einer registrierten
Frischfabrik erzeugt. Der vollstaendige Zustand wird durch alle
F/T/I/C/R/U-Intervalle getragen. M5 muss spaeter den kompletten lokalen
Zustand und ein vollstaendiges gemeinsames Feldresultat atomar ausgeben.

Eine zweite Zeitrolle, ein versteckter globaler Zustand, armweise
Initialisierung oder ein nur skalares Checkpointresultat sperrt M5.

## Rollenmatrix

| Rolle | Privater Carry | Vollstaendiges Feld erforderlich | Derzeitiger Anschlussstatus |
|---|---|---|---|
| A0 | keiner | ja | Feldhandoff offen |
| A1 | nur gemeinsames S/H-Feld | ja | neuer Lebenszyklusumschlag erforderlich |
| A2 | rollengetrennter B1-B6-Zustand | ja | neuer Lebenszyklusumschlag erforderlich |
| A3 | ein latenter Zustand pro Ort | ja | Feldhandoff offen |
| M1 | geordnete Mehrspurmenge pro Ort | ja | Funktion und Handoff fehlen |
| M2 | endlicher privater Eingabepuffer | ja | Funktion und Handoff fehlen |
| M3 | keiner | nein | passives Reduktionsschema fehlt |
| M4 | eingefrorenes Dreirollenledger | ja | neue neutrale Huelle erforderlich |
| M5 | eine Retentionskoordinate pro Ort | ja | allgemeine Funktion und Handoff fehlen |

Diese Matrix ist keine Implementierungsfreigabe. `Erforderlich` bezeichnet
nur die spaetere Vergleichsoberflaeche.

## Paketweite Fail-Closed-Regeln

Das gesamte Baselinepaket bleibt `NOT_COMPUTABLE`, wenn:

- Modell- und Orchestrierungsinformation nicht getrennt sind;
- ein Frischzustand aus einem gebrauchten Zustand rekonstruiert wird;
- Feld oder privater Zustand zwischen Armen geteilt werden;
- ein privater Zustand unvollstaendig oder ohne Digest getragen wird;
- `ALIGN_READOUT_SH` einen privaten Zustand veraendert;
- eine Ausgabe Feld und Folgezustand nicht atomar bindet;
- ein lokaler Observeroutput als vollstaendige Feldfortsetzung gilt;
- ein Handoff eine neue Dynamik oder Rueckwirkung verbirgt;
- eine Baseline Kandidatenbilanz, Armwissen oder Zukunftsdaten liest;
- eine fehlende Rolle durch Weglassen oder ein Teilergebnis ersetzt wird;
- M3 als Feldbaseline oder M2 als Kandidatenfunktion ausgefuehrt wird;
- geschlossene DTS-, T1-, G2- oder Frozen-Regeln veraendert werden.

Ein inkompatibler Handoff ist kein Kandidatenresiduum. Er stoppt den
Gesamtvergleich.

## Aussagegrenze

S1-QD definiert ausschliesslich technische Zustands- und Datengrenzen des
Pflichtbaselinepakets. Es gibt weiterhin keine neue Baselinegleichung, keine
Parameter, keine Implementierung, keinen Kandidaten und keinen Befund zu
einer hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QE - statischer Feldhandoff-Kompatibilitaetsaudit fuer A0 und A3
```

S1-QE soll ausschliesslich pruefen, ob A0 und A3 mit vorhandenen,
unveraenderten Feldabbildungen ein vollstaendiges S1-QA-Feldresultat liefern
koennen. Es darf keine neue Rueckwirkung, Gleichung, Parameter, Werte,
Implementierung, Fixture, Runtimeaenderung, Testausfuehrung oder
Ergebnisentscheidung einfuehren. Ist kein reiner Handoff vorhanden, bleiben
A0 beziehungsweise A3 gesperrt und der Pflichtbaselinevergleich kann noch
nicht ausgefuehrt werden.
