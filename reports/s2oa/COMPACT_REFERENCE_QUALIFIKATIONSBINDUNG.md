# OA: administrative Referenzkompaktierung, vorab gebunden

Qualifikation `s2oa-compact-reference-qualification-20260910-01`:
genau 16 eigenstaendige neutrale Testkoerper in einem Aufruf. Kein Retry.
Nur Darstellung redundanter IDs/Referenzen; keine neue Ereignisverarbeitung.

## Verlustfreie Darstellung

Neue OA-Huellenversion v3, Speicherform s2oa.administrative-references.v1.
Die expandierten LM-/Owner-/Paar-IDs und die v1-ID-Ableitung bleiben gleich.
Nur beim Abschluss werden administrative Wiederholungen ersetzt:

- 28 ID-Zeilen durch die explizit versionierte Formelreferenz und ihren
  expandierten Digest. Ausfuehrungswurzel bleibt separat im selben Beleg.
- Wiederholte administrative/Qualifikationspfade durch feste Rollenpfade;
  Dateinamen, Hashes und Bytezahlen bleiben individuell gebunden.
- Die Komponenten-Quellhashliste durch geordnete Indizes in die sortierte
  Hashmap der historischen Hauptqualifikation, deren voller Dateiinhalt
  weiterhin mitzaehlt. Manifest- und expandierter Listendigest werden geprueft.

Unabhaengige Expansion ohne Aufruf des Encoders oder ID-Produzenten.
Sie stellt alle Felder exakt wieder her und prueft den expandierten
Gesamtdigest. Die vorhandene technische Verifikation und fachliche Auswertung
erhalten diese expandierte Sicht; Ergebnisse referenzieren den Wire-Digest.
Memoryzustands-, Wahrnehmungs-, Formations-, Generations- und Scanpayloads
werden nicht kompaktifiziert, umklassifiziert oder numerisch neu berechnet.

## Vollstaendige Kette und unveraenderte Reserven

Historische administrative Metadaten plus beide urspruenglich bestandenen
Qualifikationen: 47135 Byte. Der fehlgeschlagene ID-Beleg bleibt separat
NOT_QUALIFIED; seine fuenf Maschinenbelege werden voll gebunden und weiter
mit 4096 Byte reserviert. Der neue Korrekturbeleg erhaelt ebenfalls hoechstens
4096 Byte, diesmal einschliesslich seines automatisch erzeugten Kurzberichts:
Vorregistrierung, Resultat, zwei Logs, Metriken, BEFUND.md. Keine Anrechnung
tatsaechlich kleinerer Dateien anstelle der gebundenen Reserve.
Damit 55327 Byte referenzierte/reservierte Metadaten VOR der Laufhuelle.
Zusaetzlich bleiben 512 Byte fuer den spaeteren Laufabschluss reserviert.

Die beiden neuen Felder-/Referenzgruppen und saemtliche Haeder/Digests zaehlen
innerhalb der 65536 Byte. Die gemeinsame Quellenzusatzhuelle bleibt 262144,
Gesamt 4194304 Byte; historische Quellenbelege voll 162321 Byte, NJ-/
Formations-/Generationsreservierung unveraendert 83968 Byte. Kein separat
beanspruchtes Vollbudget fuer einzelne Referenzdateien. Rein beschreibende
alte Berichte werden nicht neu zu Maschinenreferenzen; keine bisher in der
Bilanz enthaltene Datei wird entfernt. Die neue Abschlussdatei zaehlt mit.

Die vollstaendige gespeicherte NEUTRAL-Huelle wird ausschliesslich als
verlustfrei rekonstruierbare Struktur-/Groessenfixture gelesen. Kein Replay,
keine neue Verifikation ihrer Memory-/Feld-/Scanbefunde. Gleich lange IDs
werden eigenstaendig geprueft. Codehashkette: historische 14/14, unveraenderte
13 bestandene ID-Kontrollen im alten Fehlprotokoll, dann neue 16er-Qualifikation
der Darstellung. Der alte Fehlerstatus wird nicht pauschal akzeptiert:
exakter Fehlerbeleg und Quellendelta werden gebunden; nur der neue erfolgreiche
Korrekturbeleg kann den administrativen Anschluss entsperren.

## Getrennte neutrale Kontrollen

1. Vollstaendige Rekonstruktion, alle 28 ID-Zeilen und Unveraenderlichkeit.
2. ID-Einzelgroesse.
3. Alle 28 Laengengleichheiten.
4. Manipuliertes Metadaten-Einzellimit.
5. Manipuliertes Quellen-Einzellimit.
6. Manipuliertes Metadaten-Gesamtlimit.
7. Manipuliertes globales Gesamtlimit.
8. Volle Huelle mit beiden 4096-Reserven und 512 Berichtbytes; Direktbilanz.
9. Unabhaengiger ID-Verifikator aus rekonstruierter Tabelle.
10. Fehlende Referenz.
11. Falscher ID-Referenzdigest.
12. Vertauschte Komponentenreferenzen.
13. Fremdes Hashmanifest.
14. Verlustfreier technischer Fehlerabschluss ohne Funktionsauswertung.
15. Neue Qualifikationskette und Abwehr fremder Quellenaenderungen.
16. Geschlossene Gates und kollidierende Komponentenindizes.

Maximal 128 ID-Pruefsweeps zu 28 Zeilen und 32 administrative Roundtrips;
keine Wahrnehmungsdifferenzen, Quellenproduktion, Rezeptor-/NJ-Aufrufe,
Formationen, Scans oder Runtimeinstanzen. Preregistrierung bindet vorher
Testinventar und vollstaendige Codehashkette ueber unveraenderte Basis plus
exaktes Delta. Keine Wiederholung der alten 14 oder 20 Tests.
Gates False; ME/MI gesperrt, Prognosezweig ruhend. Hauptlauf nicht freigegeben.
