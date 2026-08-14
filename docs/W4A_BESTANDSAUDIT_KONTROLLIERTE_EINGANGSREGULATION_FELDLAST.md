# W4-A: Bestandsaudit kontrollierter Eingangsregulation bei Feldlast

Stand: 2026-08-09

Entscheidung: `REGULATION_REMAINS_CLOSED_ONE_PASSIVE_BROWSER_LOAD_GAP`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Auftrag

W4-A prueft, welche Begrenzungs-, Last- und Regulationsrollen im aktuellen
Projekt bereits vorhanden sind und ob der seit W3-M geschlossene
Browserpayloadpfad einen technisch begruendeten Anlass fuer Eingangsregulation
liefert.

Der Audit trennt strikt:

```text
technische Eingangsgrenze
!= passive Lastbeobachtung
!= adaptive Rezeptorempfindlichkeit
!= organismische Selbstregulation
```

## Bestandsmatrix

| Rolle | vorhandener Stand | Einordnung |
|---|---|---|
| PNG-Wertebereich und PCM-/Gain-Vertraege | feste Validierung kontrollierter Quellen | technische Weltgrenze, keine Regulation |
| endliche Frame-, Hop- und Dauergrenzen | feste Schutzvertraege | technische Ausfuehrungsgrenze |
| normierter Feldbereich `-1..1` | feste numerische Begrenzung | keine Ressource und keine Selbstregulation |
| Aktivierung und schneller Nachhall | beobachtbare Feldkomponenten | keine Lastressource |
| W1-R bis W1-V | passive Last-, Geometrie-, Kontrast- und Dichtecharakterisierung | keine Rueckschreibung |
| W1-W | kein Regulationsausloeser in gebundener Matrix | Regulation bleibt E0, `CONTRACT_ONLY` |
| `local_adaptive_receptivity` | festes Alpha-/Beta-/Floor-Gesetz skaliert spaetere Kontakte | entworfene adaptive Gain-Baseline, nicht aktuelle API |
| `current_api`-Graph | kein Pfad zu adaptiver Rezeptivitaet | aktive Architektur bleibt regulationsfrei |
| W3-D bis W3-M | Browserpayloadpfad, Reihenfolge und passive schnelle Spur | kein Funktions- oder Ressourcenverlust beobachtet |

## Bereits beantwortete Ausloeser

Die W1-Regulationsvorpruefung hat im gebundenen synthetischen AV-Feld keinen
der notwendigen technischen Ausloeser gefunden:

- keine erreichte oder instabile normierte Feldgrenze;
- keine unerklaerte Ueberlastung durch Geometrie;
- keine ausbleibende Entlastung ohne Kontakt;
- kein Verlust eines kleinen lokalen Kontrasts unter hoher Hintergrundlast;
- keine dichtebedingte Feldverfaelschung bis zur gebundenen Ereignisdichte;
- kein reproduzierbarer Ressourcenabbruch.

W3-D bis W3-M fuegen Reproduzierbarkeit, Browserpayloadreduktion und
Zeitordnung hinzu, zeigen aber ebenfalls keinen Funktionsverlust. Insbesondere
ist der schnelle Nachhall einseitig und kann keine Regulation begruenden.

## Geschlossene Mechaniken

Nicht wieder geoeffnet werden:

- `local_adaptive_receptivity` als Organismusfunktion;
- feste Alpha-/Beta-Absenkung mit Erholung;
- AGC, Sollaktivitaet, globaler Gain oder zentraler Controller;
- Clipping als behauptete Ressourcenregulation;
- Geraete-, Kamera-, Mikrofon- oder Betriebssystemsteuerung;
- Eingangsregulation vor einer nachgewiesenen inneren rueckwirkenden
  Substratfunktion.

Der vorhandene adaptive Rezeptivitaetscode bleibt historische
Gegenbaseline. Seine Existenz ist kein Entwicklungsauftrag.

## Genau eine offene technische Frage

Die W1-Lastmatrix verwendete synthetische reduzierte Feldkontakte. Der seit
W3-D aktuelle facade-only Browserpayloadpfad wurde dagegen nur mit moderaten
PNG-Grauwerten und PCM-Amplituden charakterisiert.

Offen ist daher ausschliesslich:

> Erhaelt der unveraenderte `current_api`-Browserpayloadpfad kleine
> kontrollierte visuelle und auditive Eingangsunterschiede auch unter hoher,
> aber weiterhin gueltiger gleichzeitiger Payloadlast, ohne die normierte
> Feldgrenze zu erreichen?

Dies ist eine passive Integrationsfrage. Ein negativer Befund wuerde zuerst
nur eine technische Schutzfrage oeffnen. Ein positiver Befund laesst
Regulation geschlossen.

## Zulaessiger W4-B-Vertrag

W4-B darf nur:

1. kontrollierte synthetische PNG- und PCM-Payloads verwenden;
2. moderate Kontrolle, hohe gemeinsame Last und hohe Last plus kleinen
   isolierten Unterschied vergleichen;
3. reduzierte Sequenzen, Aktivierungs-Linf, Grenzabstand und lokale
   Unterschiedserhaltung beobachten;
4. ohne Nachhall und mit genau der bekannten 0.5-s-Nachhallbaseline arbeiten;
5. `writes_back == false`, `substrate is None` und `development is None`
   erzwingen.

W4-B darf keinen Gain veraendern, keine Empfindlichkeit fortschreiben, keine
Regel freigeben und keinen Browser starten.

## Verwendete Projektquellen

- [Sensorische Selbstregulation: Grenzvertrag](architektur/017_SENSORISCHE_SELBSTREGULATION_GRENZVERTRAG.md)
- [Doppelte Selbstregulationsgrenze](architektur/027_DOPPELTE_SELBSTREGULATION_GRENZE.md)
- [W1-R Last und Erholung](W1R_SYNTHETISCHE_FELDBELASTUNGS_UND_ERHOLUNGSCHARAKTERISIERUNG.md)
- [W1-T massenangeglichene Geometrie](W1T_MASSENANGEGLICHENE_RAEUMLICHE_FELDGEGENBASELINE.md)
- [W1-U lokaler Kontrast unter Hintergrundlast](W1U_LOKALER_KONTRAST_UNTER_AV_HINTERGRUNDBELASTUNG.md)
- [W1-V Ereignisdichte](W1V_EREIGNISDICHTE_UND_TECHNISCHE_RESSOURCENLAST.md)
- [W1-W Regulationsabschluss E0](W1W_ABSCHLUSS_REGULATIONSVORPRUEFUNG_E0.md)
- [W2-J aktueller Importgraph](W2J_STATISCHER_ABSCHLUSSAUDIT_CURRENT_API_IMPORTGRAPH.md)
- [W3-M Abschluss des Browserpayloadkorridors](W3M_ABSCHLUSS_BROWSER_REIHENFOLGE_NACHHALLKORRIDOR.md)
- `local_adaptive_receptivity.py` als ausgeschlossene historische Baseline;
- `field_load_recovery_characterization.py` als passive Charakterisierung.

## Aussagegrenze

W4-A belegt weder notwendige Regulation noch unbegrenzte Belastbarkeit. Er
belegt keine Selbstregulation, Wahrnehmung, Feldzeit, Praegung, Memory,
Organisation, Semantik oder KI. Die Substratlinie bleibt unveraendert
pausiert. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W4-B implementiert genau eine passive facade-only Browserpayload-Last- und
Kontrastkontrolle gemaess dem oben gebundenen Vertrag. Vor einer Ausfuehrung
werden die konkreten gueltigen PNG-/PCM-Werte, der lokale Unterschied und die
Entscheidungsmetriken im Testcode explizit fixiert. Es gibt keine adaptive
Regulation und keinen Forschungslauf.

## Spaeterer Umsetzungsstand W4-B

W4-B ist am 2026-08-09 umgesetzt worden. Hohe gueltige gemeinsame
Audio-/Videolast bleibt weit unter der normierten Feldgrenze. Kleine isolierte
visuelle und auditive Unterschiede bleiben modalitaetsspezifisch und im
Endfeld messbar. Der aktive Architekturverbund besteht mit `221 passed` und
389 Subtests. Regulation bleibt unbegruendet.
