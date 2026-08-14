# S1-AA: Operativer Entwicklungsanschluss nach dem Substratstopp

Stand: 2026-08-09

Entscheidung: `FIELD_ENGINEERING_CONTINUES_SUBSTRATE_REOPENING_GATED`

Formaler Forschungslauf: nein

Runtimeaenderung: nein

## Zweck

S1-Z findet keinen vorhandenen Kandidaten fuer lokal mitentwickelte
Umformbarkeit. S1-AA verhindert daraus zwei falsche Folgerungen:

```text
nicht:
kein Substratkandidat -> Projekt beendet

und nicht:
kein Substratkandidat -> naechste beliebige Gleichung ausprobieren
```

Stattdessen werden die belastbare technische Feldentwicklung und die
pausierte Substratforschung operativ getrennt.

## Linie A: aktive Feld-Engineeringlinie

Aktiv bleibt die technische Architektur:

```text
kontrollierte Browser-/Video-/Audio-Testwelt
-> Rezeptorsequenzen
-> neutraler Verteiler und offene Docks
-> gemeinsames MCM-Feld
-> S/H-Feldzustand
-> optionaler transparenter F3-Referenzarm
-> Snapshot und passive technische Beobachtung
```

Diese Linie darf weiterentwickeln:

- reproduzierbare kontrollierte AV-Testweltvertraege;
- eine eindeutige aktuelle Paket- und Sitzungsoberflaeche;
- kausale Zeituebergabe und atomare Feldschritte;
- Snapshot, Restore, Teilung und Wiederaufnahme;
- passive Diagnose und Komponentenbilanzen;
- technische Stabilitaets-, Ressourcen- und Kompatibilitaetskontrollen;
- F3, lineare Kopplung und Nullpfad als explizit benannte Referenzarme.

Sie darf nicht behaupten, dadurch Memory, Lernen, Feldzeit, innerer Kontext,
Organisation, Semantik, Selbstregulation oder KI zu entwickeln.

## Linie B: pausierte Substratforschung

Nicht weitergefuehrt werden:

- neue L-, Q-, M- oder sonstige langsame Zustaende;
- weitere Mobilitaets-, Gain-, Hysterese- oder Attraktorvarianten;
- adaptive Kanten, Kontaktbewegung oder Zieltopologie;
- eine zweite MCM-Runtime als Memoryschicht;
- Memory-Lebenszykluslaeufe ohne zugelassenen Kandidaten;
- Feldzeit-, Praegungs-, Cluster- oder Reflexionsmechaniken;
- Runtimegerueste fuer eine noch nicht begruendete Substratphysik.

Die vorhandenen Module und Dokumente bleiben als historische Evidenz,
Regression oder Pflichtbaseline erhalten. Ihr Vorhandensein ist keine aktive
Architekturfreigabe.

## Hartes Wiedereroeffnungstor

Die Substratlinie darf erst wieder geoeffnet werden, wenn ein einziger
konkreter Vorschlag vor jeder Implementierung alle folgenden Punkte bindet:

1. **Unabhaengige Naturrolle:** Die Zustands- oder Materialfunktion ist auch
   sinnvoll, wenn sie niemals Memory hervorbringt.
2. **Lokale Ursache:** Eine vorhandene lokale MCM-Groesse wirkt als klar
   benannte Ursache; ein gewuenschtes Ergebnis ist keine Ursache.
3. **Konjugierte Rueckwirkung:** Dieselbe Wechselwirkung erklaert, wie der
   veraenderte Zustand auf das gemeinsame Feld zurueckwirkt. Getrennte
   Schreib- und Leserregeln sind unzulaessig.
4. **Endlichkeit und Bilanz:** Wertebereich, Ressource, Erhaltung oder
   Dissipation besitzen eine fachliche Begruendung und pruefbare Grenzen.
5. **Vorhersage vor Memory:** Der Vorschlag schliesst mindestens einen
   technisch moeglichen Verlauf aus, bevor R1 bis R4 ausgewertet werden.
6. **R4 nur ermoeglicht:** Dieselbe unveraenderte Naturform kann prinzipiell
   alte Wirkung unter konkurrierender Weltgeschichte funktionslos und die
   Kapazitaet anders nutzbar machen; sie schreibt diesen Lebenszyklus nicht
   als Phasenregel vor.
7. **Statische Nichtreduktion:** F3, Leaky-Spur, Produktintegrator, fester
   Leser, adaptive Mobilitaet, Hysterese, Attraktor und Standardmaterialklasse
   erklaeren die Rolle nicht gleichwertig.
8. **Darstellungsoffenheit:** Keine Objekt-, Partner-, Episoden-, Cluster-,
   Modalitaets- oder Bedeutungskennung ist erforderlich.
9. **Nullpfad:** Eine vorregistrierte Ablation reproduziert die heutige
   Feldruntime exakt.
10. **Neue Benutzerentscheidung:** Erst nach bestandenem statischem Audit
    darf eine konkrete Gleichung oder Implementierung beauftragt werden.

Ein fehlender Punkt bedeutet `STOPP`. Komplexitaet, biologische Analogie oder
ein erwarteter Memorynutzen ersetzen keinen Punkt dieses Tors.

## Trennung von Engineering und Forschung

| Arbeit | Einordnung | Laufnummer |
|---|---|---|
| API-, Vertrags-, Snapshot- oder Reproduzierbarkeitstest | technische Entwicklung | nein |
| F3-/Baseline-Kompatibilitaet ohne neue Funktionsaussage | technische Entwicklung | nein |
| passive Diagnose bekannter Gleichungsbeitraege | technische Entwicklung | nein |
| neuer Kandidat nach bestandenem Wiedereroeffnungstor | neue Forschungsfrage | erst nach Vorregistrierung |
| Memory-, R4-, Feldzeit- oder Organisationsaussage | Forschung | nur mit Kandidat, Baselines und Freigabe |

## Aktuelle technische Bereinigungsfrage

Die Paketoberflaeche enthaelt nebeneinander:

- aktuelle kontrollierte Testwelt- und gemeinsame Feldmodule;
- Live-Kamera- und Live-Audioadapter;
- historische Z4-Ausfuehrungspfade;
- suspendierte oder geschlossene Memory- und Materialkandidaten;
- einmalige Runner- und Abnahmewerkzeuge.

Diese Koexistenz im Repository ist als Forschungsarchiv zulaessig. Sie darf
aber nicht bedeuten, dass alle Module zur aktuellen produktiven Architektur
gehoeren. Vor jeder weiteren technischen Integration muss deshalb die
oeffentliche aktuelle API gegen historische und geparkte Oberflaechen
abgegrenzt werden.

## Testwelt- und Zweiggrenze

- Vorerst nur kontrollierte Browser-, Video- und Audio-Testwelten sowie
  kontrollierte audiovisuelle Dateien.
- Keine Kamera, kein Live-Mikrofon und keine physische Sensorik im aktiven
  Entwicklungsweg.
- Historische Live-Adapter duerfen im Repository verbleiben, werden aber
  nicht als aktuelle API behandelt.
- Z4, Lauf 197 und 213ZZR bis 213ZZU bleiben unberuehrt.
- Der Orchestrator bleibt bis zu einer spaeteren gezielten Neukonfiguration
  pausiert.

## Aussagegrenze

S1-AA ist ein Projekt- und Architekturentscheid. Er erzeugt keinen neuen
Feldbefund und keinen Nachweis von Memory, Lernen, relativer Feldzeit,
innerem Kontext, Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

W2-A erstellt einen statischen Bestandsaudit der oeffentlichen
Paketoberflaeche. Er ordnet jeden Export und jede direkt angebotene
Sitzungsfunktion genau einer Kategorie zu:

```text
CURRENT_CONTROLLED_FIELD_API
REFERENCE_ONLY
HISTORICAL_OR_PAUSED
LIVE_OR_PHYSICAL_INACTIVE
PRIVATE_TOOLING
```

W2-A veraendert noch keine Importe und loescht keine Module. Ergebnis ist
eine kleine Solloberflaeche fuer kontrollierte Testwelt, gemeinsames Feld,
Snapshot und optionale F3-Referenz sowie eine konkrete Liste der Exporte, die
spaeter aus der aktuellen Paketoberflaeche herausgeloest werden sollten.
