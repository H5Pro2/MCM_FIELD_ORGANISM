# S2-LS Read-only Ursachenbefund

## Status und Grenze

- Audit-ID: `s2ls-readonly-cause-audit-20260904-03`
- Status: `S2LS_READONLY_CAUSE_AUDIT_COMPLETE`
- Unveraenderte Quelle: `s2ls-real-presealed-av-corpus-20260904-01`
- Aufrufe im Audit: Memory `0`, Rezeptor `0`, Kontext `0`, Feld `0`
- Keine Schwelle, Quelle oder bestehende Ergebnisdatei wurde geaendert.
- Der Audit ist ein Ursachenbefund des vorhandenen Resultats, kein neuer Funktionslauf.

Der erste Auditversuch `...-01` endete vor jeder Artefakterzeugung an einer zu
engen Fast-Rekonstruktionsannahme. `...-02` bleibt unveraendert erhalten, ist aber
wegen der zunaechst semantisch verwendeten supportgesaettigten Ereignisbezeichnung
durch `...-03` ersetzt.

## Formationsspur

Die Tabelle nennt die aus Vorbelegung, Quelldistanz und gebundener Schwelle
abgeleitete effektive Operation. Die S2-LS-Projektion bezeichnet ein Update nach
Erreichen des maximalen Supports als `REPLACED`; diese Bezeichnung ist fuer die
Linienrekonstruktion nicht massgeblich.

| Nr. | Inhalt | Fast | Auditory PPB | Visual PPB |
|---:|---|---|---|---|
| 1 | `content-001` | `CREATED` | `NO_UPDATE` | `NO_UPDATE` |
| 2 | `content-007` | `MATCHED` | `CREATED slot.000` | `CREATED slot.000` |
| 3 | `content-002` | `MATCHED` | `CREATED slot.001` | `MATCHED slot.000` |
| 4 | `content-008` | `MATCHED` | `MATCHED slot.000` | `MATCHED slot.000` |
| 5 | `content-003` | `MATCHED` | `MATCHED slot.001` | `MATCHED slot.000` |
| 6 | `content-009` | `MATCHED` | `MATCHED slot.000` | `MATCHED slot.000` |
| 7 | `content-004` | `MATCHED` | `MATCHED slot.001` | `MATCHED slot.000` |
| 8 | `content-010` | `MATCHED` | `MATCHED slot.000` | `MATCHED slot.000` |
| 9 | `content-013` | `MATCHED` | `CREATED slot.002` | `MATCHED slot.000` |
| 10 | `content-014` | `MATCHED` | `CREATED slot.003` | `MATCHED slot.000` |
| 11 | `content-015` | `MATCHED` | `CREATED slot.004` | `MATCHED slot.000` |
| 12 | `content-016` | `MATCHED` | `CREATED slot.005` | `MATCHED slot.000` |
| 13 | `content-017` | `MATCHED` | `CREATED slot.006` | `MATCHED slot.000` |
| 14 | `content-018` | `MATCHED` | `MATCHED slot.000` | `MATCHED slot.000` |
| 15 | `content-019` | `MATCHED` | `CREATED slot.007` | `MATCHED slot.000` |
| 16 | `content-020` | `MATCHED` | `REPLACED slot.001` | `MATCHED slot.000` |
| 17 | `content-021` | `MATCHED` | `REPLACED slot.002` | `MATCHED slot.000` |

Alle 17 Fast-Schritte selektierten `tspm1.fast.slot.000`. Der erste Schritt legte
ihn an; die folgenden 16 Schritte waren nach der echten gemeinsamen Fast-Regel
Updates. Die Binary64-Fortschreibung mit Faktor `0.5` reproduziert jeden
aufgezeichneten Post-Wertedigest.

## Druckeinfluss

- Visuell aktualisierten `content-013` bis `content-021` ausnahmslos den bereits
  gemeinsam von Family-01 und Family-02 belegten `slot.000`. Die Distanzen lagen
  zwischen `0.001809832168` und `0.002161445911`, also unter `0.01`.
- Auditiv aktualisierte `content-018` den stabilen Family-02-`slot.000` bei
  `0.016987886152` und veraenderte damit dessen Prototyp.
- Auditiv ersetzte `content-020` den stabilen Family-01-`slot.001` bei
  `0.040816988265`; danach war dieser Slot nur noch Support `1`.
- Die uebrigen auditiven Druckinhalte legten eigene instabile Slots an oder
  ersetzten bereits instabile Druckslots.

Der adaptive auditive Family-02-Treffer ist deshalb kein isolierter Familienbefund:
sein finaler stabiler Prototyp enthaelt eine Druckaktualisierung. Der ehemalige
Family-01-Prototyp ist im Endbestand nicht mehr stabil vorhanden.

## Treffermengen der acht Hinweise

| Hinweis | Modalitaet | B4-Treffer | Fast-Treffer | Stable-Treffer | Entscheidung |
|---|---|---:|---:|---:|---|
| `content-005` | visuell | 0 | 0 | 0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| `content-005` | auditiv | 9 | 1 | 0 | `ABSTAIN_INTERNAL_AMBIGUITY` |
| `content-006` | visuell | 0 | 0 | 0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| `content-006` | auditiv | 9 | 1 | 0 | `ABSTAIN_INTERNAL_AMBIGUITY` |
| `content-011` | visuell | 0 | 0 | 0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| `content-011` | auditiv | 9 | 1 | 1 | `ABSTAIN_INTERNAL_AMBIGUITY` |
| `content-012` | visuell | 0 | 0 | 0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| `content-012` | auditiv | 9 | 1 | 1 | `ABSTAIN_INTERNAL_AMBIGUITY` |

Damit ist die auditive Enthaltung konkret durch die breite A-Seite verursacht:
jeder auditive Hinweis trifft alle neun B4-Eintraege und den einen Fast-Slot.
Family-02 trifft zusaetzlich den druckaktualisierten stabilen Slot.

## Vollvektor gegen maskierten Scan

Der einzige stabile visuelle Prototyp liegt fuer alle vier Holdouts nach
Vollvektor-L1 klar innerhalb der Slow-Schwelle `0.01`:

| Inhalt | Vollvektor-L1 | L1 auf 32 sichtbaren Positionen | Exakte Abweichungen |
|---|---:|---:|---:|
| `content-005` | `0.001736472642` | `0.001932965611` | `32/32` |
| `content-006` | `0.001730432147` | `0.001963286850` | `32/32` |
| `content-011` | `0.000775782216` | `0.000857056792` | `32/32` |
| `content-012` | `0.000783571319` | `0.000890319546` | `32/32` |

Der visuelle Teilscan verlangt dagegen exakte Gleichheit an jeder sichtbaren
Position. Deshalb liefert er trotz kleiner L1-Distanzen fuer B4, Fast und Slow
jeweils null Treffer. Vollvergleich und Teilhinweisregel bilden auf diesem Korpus
somit keine kompatible Anwendbarkeitsdefinition.

## Verlust visueller Struktur

Die 288 Blockmittelwerte behalten auf diesem Korpus nur einen kleinen Anteil der
absoluten Pixel-L1-Distanz:

| Vergleich | Rohes RGB-L1, Mittel | 288er-L1, Mittel | erhaltener Anteil |
|---|---:|---:|---:|
| innerhalb einer Familie | `0.020833609237` | `0.000138179273` | `0.6633 %` |
| zwischen Family-01 und Family-02 | `0.334536961547` | `0.002263106410` | `0.6765 %` |
| Holdout zu eigener Familie | `0.020833092916` | `0.000140626103` | `0.6750 %` |
| Druckinhalt zu Training | `0.334674065557` | `0.002254828537` | `0.6737 %` |

Ueber alle 21 Quellen betraegt die mittlere absolute Abweichung der Pixel von
ihrem jeweiligen Blockmittel `0.250985862861`; die mittlere blockinterne
Standardabweichung betraegt `0.289807709874`. Diese Struktur ist im 288er-Vektor
nicht enthalten. Insbesondere bleibt die reduzierte mittlere Distanz zwischen den
beiden Texturfamilien mit `0.002263106410` deutlich unter der visuellen
Slow-Schwelle `0.01`.

## Schlussfolgerung

Der vorhandene Lauf belegt korrektes fail-closed Verhalten. Seine fehlende
praktische Kontextnutzung hat drei getrennte Ursachen:

1. visuelle Blockmittelung komprimiert die relevante Texturvariation unter die
   bestehende Slow-Schwelle und fuehrt zu einem gemeinsamen visuellen Prototyp;
2. der exakte sichtbare Positionsscan ist strenger als die L1-basierte
   Vollvektorzuordnung und lehnt alle vier visuellen Holdouts ab;
3. die breite auditive A-Schwelle erzeugt fuer jeden Hinweis zehn interne
   A-Treffer, waehrend Druckereize einen stabilen auditiven Familienprototyp
   aktualisieren und den anderen ersetzen.

Das Ergebnis begruendet keine neue Memoryebene und keine Schwellenkorrektur. Ein
spaeterer Vergleich einer minimalen visuellen Strukturbaseline muss auf einem neu
vorab versiegelten Korpus gegen die unveraenderte Blockmittelung erfolgen.

## Bindungen

- S2-LS-Ergebnisdatei SHA-256:
  `2be76afc69f7d587cd1098895915c905d8d5349bb6795e3dde903f71744d4fc1`
- S2-LS-Recorddigest:
  `c939b15dae96b8a6c17be2f09936f70043e56d055624159ece6d862c976fface`
- Auditdigest:
  `51d68b7858b434e5939e122122ec40d61be9cad0dca94485916937273cfd1f7b`
- Auditdatei SHA-256:
  `cc3abb50a2caeefd1391b6f696bed41597099f3c8b2a77fa99a5d6436d2f1670`
