# W4-B: Browserpayload Last-/Kontrast-Nullpruefung

Stand: 2026-08-09

Entscheidung: `HIGH_VALID_BROWSER_LOAD_RETAINS_SMALL_MODAL_DIFFERENCES`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W4-B prueft die in W4-A isolierte Integrationsfrage: Bleiben kleine visuelle
und auditive Eingangsunterschiede im unveraenderten facade-only
Browserpayloadpfad unter hoher, aber gueltiger gemeinsamer Audio-/Videolast
erhalten?

## Gebundene Lastmatrix

```text
moderate gemeinsame Last:
  drei uniforme PNG-Frames mit Grauwert 128
  15 PCM-Hops mit 100 Hz und Amplitude 0.25

hohe gemeinsame Last:
  drei uniforme PNG-Frames mit Grauwert 230
  15 PCM-Hops mit 100 Hz und Amplitude 0.85

kleiner visueller Unterschied unter hoher Last:
  nur Rot der linken oberen 2x2-Rezeptorzelle: +5 PNG-Stufen

kleiner auditiver Unterschied unter hoher Last:
  nur Amplitude des vorhandenen 100-Hz-Tons: 0.85 -> 0.87
```

Alle vier Arme werden einmal ohne Nachhall und einmal mit der bekannten
neutralen Nachhallzeit von 0.5 s frisch aufgebaut. Es gibt keine
Rueckschreibung oder adaptive Zustandsgroesse.

## Ergebnis

| technische Groesse | Wert |
|---|---:|
| moderate Last, Aktivierungs-Linf | 0.13009370977532214 |
| hohe Last, Aktivierungs-Linf | 0.23376229256208123 |
| Grenzabstand der hohen Last | 0.7662377074379187 |
| visuelles Aktivierungsdelta Linf | 0.004026324124621894 |
| auditives Aktivierungsdelta Linf | 0.0030802357351674137 |

Fuer beide Nachhallbedingungen gilt:

- hohe gemeinsame Last erzeugt mehr Aktivierung als moderate Last;
- kein Arm erreicht die normierte Feldgrenze;
- der visuelle Unterschied veraendert nur die visuelle reduzierte Sequenz;
- der auditive Unterschied veraendert nur die auditive reduzierte Sequenz;
- beide Unterschiede bleiben im End-Aktivierungsvektor messbar;
- Substrat und Entwicklung bleiben abwesend.

Mit 0.5 s Nachhall bleiben beide Unterschiede auch im passiven
Nachhallvektor messbar. Ohne Nachhall bleibt dieser global null.

## Entscheidung

Der aktuelle Browserpayloadpfad zeigt im gebundenen hohen Lastbereich keinen
Verlust der kleinen kontrollierten Weltunterschiede und keine Naehe zur
normierten Feldgrenze. W4-B liefert daher keinen technischen Anlass fuer Gain,
Clipping, adaptive Empfindlichkeit oder andere Eingangsregulation.

## Verifikation

```text
gezielter Consumertest: 10 passed
aktiver Architekturverbund: 221 passed
389 subtests passed
Aktivierungs-Linf in allen Armen < 1.0
visuelle Modalitaetsisolation erhalten
auditive Modalitaetsisolation erhalten
substrate is None
development is None
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- [W4-A Regulations- und Lastaudit](W4A_BESTANDSAUDIT_KONTROLLIERTE_EINGANGSREGULATION_FELDLAST.md)
- W3-D bis W3-M als facade-only Browserpayloadpfad;
- `current_api` als einziger Projektimport des Consumers;
- kontrollierte synthetische PNG- und PCM-Payloads;
- oeffentliche reduzierte Sequenzen und Feldsnapshotkomponenten.

## Aussagegrenze

W4-B gilt nur fuer die gebundenen Werte, Geometrie, Frequenz und Dauer. Er
belegt keine unbegrenzte Belastbarkeit und keine Selbstregulation. Er belegt
kein Memory, Lernen, Feldzeit, inneren Kontext, Organisation, Semantik oder
KI. Es wurde kein Browser oder Playwright gestartet und keine Kamera, kein
Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W4-C schliesst die Regulations- und Lastlinie statisch ab:

1. W1-R bis W1-W und W4-A/B in einer Ausloesermatrix zusammenfuehren;
2. technische Schutzgrenzen von organismischer Regulation getrennt halten;
3. adaptive Rezeptivitaet, Gain, Clipping und Controller geschlossen lassen;
4. keine weitere Laststeigerung ohne vorher deklarierten Zielkorridor oder
   reproduzierbaren Funktionsverlust vorbereiten;
5. den naechsten Projektbereich aus einer anderen offenen Architekturluecke
   ableiten.

## Spaeterer Abschlussstand W4-C

W4-C ist am 2026-08-09 statisch gebunden worden. Im kontrollierten Bereich
liegt kein technischer Regulationsausloeser vor. Adaptive Rezeptivitaet und
weitere ungezielte Laststeigerung bleiben geschlossen. Der naechste
Projektanschluss ist ein enger Primaerquellen-Suchvertrag fuer eine
unabhaengige lokale Substratnatur.
