# OA-ID-Anschluss: NOT_QUALIFIED

Qualifikations-ID `s2oa-event-id-qualification-20260910-01`.
Genau ein neutraler Testaufruf, Exit 1; 14 Testkoerper erreicht,
13 bestanden, ein Fehler in test_13_complete_envelope. Kein Retry.

## Implementierter Anschluss

Plan-IDs e01..e28 und historische Quellen unveraendert.
`s2oa.event-id-binding.v1` bindet ordinal, plan_id und technical_id
an die Ausfuehrungswurzel; technische ID `s2oa-event-eNN`.
OA-Gesamthuelle v2, historische Kern-/NEUTRAL-Typen unveraendert.
Materialisierer, Eingangspruefung und unabhaengige ID-Verifikation
nutzen die Zuordnung. AV-Paar/Owner/Consume erhalten daraus technische
IDs; Auswertung und Quellen behalten Plan-IDs. Das vollstaendige
statische Anschlussinventar steht in ../EVENT_ID_QUALIFIKATIONSBINDUNG.md.

Die alte 14/14-Qualifikation wird nur gegen ihre alten Quellhashes
gebunden. Zwei geaenderte Hauptanschlussdateien und vier neue Dateien
gehoeren zum neuen Delta, nicht zur historischen Pruefdeckung.
Der Haupteinstieg verlangt dessen bestandenen Beleg: aktuell gesperrt.

## Erreicht und nicht erreicht

Alle 28 Zuordnungen gueltig/eindeutig; fehlende, vertauschte,
kollidierende und fremde Bindungen typisiert abgewiesen. Separater
ID-Verifikator ohne produktive Ableitungshelfer. Kurze Plan-ID e01
erreichte mit neutralem 288er-Nullkontakt ueber bind_event den echten
visuellen LM-Builder als s2oa-event-e01; Offline-Decodierung und
Quellenbelegpruefung bestanden. Eingang unveraendert. Keine OA-Payloads,
Rezeptor-/NJ-Aufrufe, Formationen, Scans oder Runtimeinstanzen.

Pruefung 13 erreicht b.envelope_size fuer die vollstaendige gespeicherte
NEUTRAL-Groessenfixture mit neuer ID-/Qualifikationshuelle, kein Replay
und keine neue Verifikation der historischen Geschichte.
Die anschliessende Reserveassertion scheitert:

| Bilanz | Byte |
| --- | ---: |
| Metadaten mit gebundener neuer Qualifikationsreserve | 65289 |
| Zusaetzliche vorab gebundene Abschlussberichtreserve | 512 |
| Erforderlich zusammen | 65801 |
| Unveraenderte Metadatengrenze | 65536 |
| Ueberschreitung | 265 |

Teststelle: tests/test_s2oa_private_event_ids.py:176.
Keine Grenz- oder Reservenaenderung. Die spaeteren Assertions dieser
Gruppe (ID-Einzelgroesse, Laengengleichheit, manipulierte Einzel-/
Gesamtbudgets) wurden nicht erreicht. Test 14 lief danach erfolgreich.
Die volle Qualifikation ist nicht bestanden; keine Hauptlaufbereitschaft.

## Belege und Grenzen

Vorregistrierung 1919, Resultat 886, stderr 757, stdout 0, Metriken 89 Byte:
zusammen 3651/4096 Byte fuer die fuenf neuen referenzierten Dateien.
Dieser Istwert ersetzt nicht nachtraeglich die im Huellentest gebundene
Reserve. Neutraler gepackter e01-Eingang 5298/16384 Byte;
Quellenreceipt 174/1024 Byte. Vollstaendige neue Groessenmetriken
wurden nach der gescheiterten Assertion nicht veroeffentlicht.

Quellinventar vor/nach unveraendert, Gesamtdigest:
`d91b96b43fb9950c6ee5d4a4d24faf11d36fef68cebacd23c55ba5d469efd7d3`.
Ergebnisdigest:
`9ba20ce38d5c6f19f0f4e19efe00958bfe7e5bab5584ae4098dd56322f42fce8`.
Vollstaendige Einzelhashes sind ueber historische Vorregistrierung
und das explizite neue Delta gebunden. Keine weitere Qualifikation.

Alter OA-Lauf bleibt NOT_EVALUABLE; dessen historische Ausloesestelle
weiterhin nicht unmittelbar belegt. Kein alter Fehlerbeleg erneut
geprueft. Gates False, ME/MI gesperrt, Prognosezweig ruht.

RUECKMELDUNG ERFORDERLICH: Allenfalls weitere redundante administrative
ID-/Referenzangaben digestgebunden kompakt darstellen, ohne Inhalte
aus der Gesamtbilanz zu entfernen. Keine Grenzerhoehung, keine
nachtraegliche Reduktion der gebundenen Berichtreserve; erst separate
Entscheidung ueber Korrektur und erneute fokussierte Qualifikation.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zur
um 265 Byte ueberschrittenen Metadatenhuelle weiter.
