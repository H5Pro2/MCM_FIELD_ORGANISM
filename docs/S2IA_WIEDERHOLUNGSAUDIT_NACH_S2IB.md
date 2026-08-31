# S2-IA - Wiederholungsaudit nach S2-IB

## Status

`S2IA_REPEAT_AUDIT_PASSED_PRIVATE_IMPLEMENTATION_ELIGIBLE`

Der vollstaendige statische Materialisierungs- und
Nichtzirkularitaetsaudit wurde gegen den S2-IB-Korrekturvertrag wiederholt.
Alle drei Blocker aus dem ersten S2-IA-Audit sind geschlossen.

S2-IB-Vertragsdigest:
`dca7ecfe8822f1fceb49381a7b4ced12c535b74e9eb5b4089c63bbaf4eb9a54d`

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Probe-, Speicher-, Verbraucher- oder Zustandsfunktion aufgerufen.

## IA-B01 - Statusdomain geschlossen

Die korrigierte Statusfunktion besitzt exakt fuenf regulaere Werte:

```text
NO_CONTEXT
NO_APPLICABLE_CONTEXT
SINGLE_SOURCE
CONSISTENT
CONFLICT
```

Fuer die drei moeglichen Bereichslagen `APPLICABLE`, `ABSENT_VALID` und
`VISIBLE_CONFLICT` wurden alle 3x3 A/B-Kombinationen statisch enumeriert. Der
Fall mit zwei anwendbaren Kandidaten besitzt wegen gleicher oder verschiedener
Maskenergaenzungen zwei Unterpfade. Damit entstehen exakt zehn
Entscheidungspfade.

Die Abbildung ist vollstaendig und exklusiv:

- `NO_CONTEXT` tritt genau und nur bei zweimal `ABSENT_VALID` auf;
- `NO_APPLICABLE_CONTEXT` tritt genau bei keinem anwendbaren, aber mindestens
  einem gueltig vorhandenen Kandidaten auf;
- `SINGLE_SOURCE` tritt genau bei einem anwendbaren Kandidaten auf;
- `CONSISTENT` und `CONFLICT` treten nur bei zwei anwendbaren Kandidaten auf
  und werden ausschliesslich aus den neun maskierten Ergaenzungswerten
  unterschieden;
- beschaedigte Evidenz besitzt keinen regulaeren Statuspfad.

Der fruehere C8-Widerspruch ist geschlossen:

```text
VISIBLE_CONFLICT + VISIBLE_CONFLICT
-> NO_APPLICABLE_CONTEXT
```

## Vorhandene Daten und Erreichbarkeit

Die konkreten vorhandenen Datentypen liefern alle benoetigten Quellen:

- `TwoAreaContextBundle` bindet Probe, Quelle, Konfiguration,
  Composite-Zustand, Vor-/Nachzustand und genau die Bereiche A und B;
- A liefert den oeffentlichen `B4_RECENT`-Kandidaten als eine gemeinsame
  AV-Komponente mit 26 Werten;
- B liefert den `TSPM_SLOW`-Kandidaten und dessen eindeutig stabile visuelle
  Komponente mit 18 Werten;
- beide Rollen liefern Finding-, Kandidaten-, Komponenten- und
  Komponentenquelldigests;
- `ABSENT_VALID` ist ohne erfundenen Kandidaten vorhanden;
- die maskierte Probe bindet exakt neun sichtbare und neun maskierte
  Positionen.

Alle zehn korrigierten Matrixfaelle sind technisch erreichbar:

- gleicher aktueller und stabiler Inhalt fuer `CONSISTENT`;
- der S2-HY-Spiegelkonflikt fuer `CONFLICT`;
- frischer A-Inhalt ohne Slow-Kandidat fuer A-only;
- stabiler B-Inhalt nach Entfernung aus A fuer B-only;
- zweimal gueltige Abwesenheit fuer `NO_CONTEXT`;
- je ein passender und ein sichtbar widerspruechlicher Kandidat fuer die
  beiden `SINGLE_SOURCE`-Kontrollen;
- ein oder zwei sichtbar widerspruechliche Kandidaten fuer die drei
  `NO_APPLICABLE_CONTEXT`-Kontrollen.

Die Fall-ID und der Sollstatus werden fuer keine Materialisierung benoetigt.
Sie bleiben ausschliesslich nachgelagerte Auswertungsevidenz.

## IA-B02 - Ownerbindung geschlossen

Jeder einzelne Signalaufruf besitzt exakt einen privaten Owner. Dieser bindet
vor O1 die ownerfreie Eingabe und endet atomar in `CONSUMED` oder `FAILED`.

Die urspruenglich moegliche Input-/Owner-Rueckkante ist ausdruecklich
ausgeschlossen:

```text
Probe + Bundle
-> ownerfreie Inputbindung / input_digest
-> Owner READY / owner_prestate_digest
```

Der Owner bindet anschliessend Probe, A-/B-Befunde, Vergleich und Ergebnis
ueber denselben Eingabedigest. Es gibt keine Unterowner und keine
Teilveroeffentlichung.

Erfolg:

```text
Result
-> Owner CONSUMED
-> atomares Tupel aus Result, Receipt und Owner-Nachzustand
```

Fehler:

```text
Fehlerursache
-> Owner FAILED
-> atomares ErrorReceipt ohne regulaeres Ergebnis
```

Ownerzustand, ID- und Invocation-Grenzen, Einmalverbrauch, Endzustaende und
Wiederverwendungsverbot sind vollstaendig gebunden. Signalgeber und
Direktbaseline besitzen getrennte Ownerinstanzen derselben Form; innerhalb
eines Aufrufs bleibt es genau ein Owner.

## Datenformen und Digestgraph

S2-IB bindet unveraenderliche Formen fuer:

- ownerfreie Eingabe;
- Owner-Vor- und Nachzustand;
- A- und B-Anwendbarkeitsbefund;
- Maskenergaenzungsvergleich;
- Ressourcenledger;
- Ergebnis;
- Erfolgsreceipt;
- Fehlerursache und ErrorReceipt.

Alle optionalen Felder besitzen statusabhaengige Invarianten. Insbesondere
kann `ABSENT_VALID` keine Kandidatenwerte tragen, `VISIBLE_CONFLICT` keine
Maskenergaenzung liefern und nur `APPLICABLE` einen Maskenwertdigest erzeugen.

Der statische Graph ist vollstaendig vorwaertsgerichtet:

```text
Input
-> Owner READY
-> A-Finding und B-Finding als Geschwister
-> Vergleich
-> Ledger
-> Result
-> Owner CONSUMED
-> Receipt
```

Der Fehlergraph verwendet einen eigenen Fehlerursachendigest vor dem
Owner-Nachzustand. Kein Objekt bindet den eigenen oder einen spaeteren Digest.
Sollstatus und Zielwerte sind keine Eltern des Funktionsgraphen.

## Symmetrie

Die zehn Statuspfade wurden mit A/B und B/A statisch verglichen. Fuer jede
Vertauschung bleiben erhalten:

- regulaerer Status;
- Vergleichsstatus `NOT_PERFORMED`, `EQUAL` oder `DIFFERENT`;
- Menge der abweichenden Maskenpositionen;
- Ressourcenledger;
- Zahl vorhandener und anwendbarer Kandidaten.

Nur die transparenten Rollenangaben in `present_areas` und
`applicable_areas` werden entsprechend vertauscht. Die kanonische
Serialisierungsreihenfolge A vor B erzeugt keine funktionale Praeferenz.

## IA-B03 - Exakte Ledger geschlossen

Fuer `P = vorhandene Kandidaten` und `K = anwendbare Kandidaten` wurden alle
zulaessigen Pfade statisch materialisiert:

| P | K | sichtbare Vergleiche | Maskenwerte | A/B-Vergleiche | validierte Bindungsdigests | neue Digests |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 0 | 15 | 7 |
| 1 | 0 | 9 | 0 | 0 | 18 | 7 |
| 1 | 1 | 9 | 9 | 0 | 18 | 8 |
| 2 | 0 | 18 | 0 | 0 | 21 | 7 |
| 2 | 1 | 18 | 9 | 0 | 21 | 8 |
| 2 | 2 | 18 | 18 | 9 | 21 | 9 |

Jeder Pfad besitzt zusaetzlich exakt eine Eingabevalidierung, 18
Probenpositionsvalidierungen, eine Bundlevalidierung, zwei Bereichslookups,
zwei Bereichsfindingvalidierungen, sechs logische Operationen und null
Speicher- oder Lernaufrufe.

Signalgeber und Direktbaseline verwenden dieselben Formeln und Grenzen. Eine
gueltige Abwesenheit oder ein sichtbarer Konflikt reduziert nur die
tatsaechlich notwendige Projektionsarbeit; kein anderer Zaehlwert wird dafuer
erhoeht.

## Kanonische Groessenpruefung

Die vollstaendigen typisierten Worst-Case-Huellen wurden statisch mit
96-Zeichen-IDs, 64-Zeichen-Digests, maximal neun Positionen, dem laengsten
Status beziehungsweise Rollenwert und neun hochpraezisen endlichen
Floatwerten berechnet.

| Form | Berechnete Bytes | Vertragsgrenze | Reserve |
| --- | ---: | ---: | ---: |
| Owner-Nachzustand | 678 | 768 | 90 |
| Eingabe | 1243 | 1792 | 549 |
| Anwendbarkeitsbefund | 1261 | 2048 | 787 |
| Vergleich | 688 | 1280 | 592 |
| Ledger | 628 | 1536 | 908 |
| Ergebnis | 1201 | 2048 | 847 |
| Erfolgsreceipt | 1007 | 2048 | 1041 |
| Fehlerursache | 554 | 1024 | 470 |
| ErrorReceipt | 694 | 1536 | 842 |

Alle Werte enthalten den kanonischen ASCII-Zeilenabschluss. Keine Form
erreicht 4095 Byte. Vollstaendige Probe-, Bundle-, Kandidaten- oder
Speicherobjekte werden nicht erneut eingebettet; Receipts binden sie nur ueber
typisierte Digests.

Die alleinige Ablehnungsstelle fuer eine Groessen- oder Ledgerabweichung liegt
in O5 vor der atomaren Veroeffentlichung O6.

## Baseline und Falsifikation

Die Direktbaseline ist mit denselben Eingaben, derselben Statusfunktion,
demselben Ownerformat und identischen Ledgerformeln materialisierbar. Sie darf
den Signalgeber oder dessen Ergebnis nicht aufrufen. Der Signalgeber darf
umgekehrt kein Baselineergebnis verwenden.

Ein spaeter gueltiger Funktionsbefund muss Signal und Baseline fuer alle zehn
Statuspfade sowie deren A/B-Vertauschungen vergleichen. Abweichung,
Zustandsaenderung, Teilveroeffentlichung, Auswahl, Rangfolge oder Fallback ist
eine funktionale Falsifikation beziehungsweise bei Bindungsbruch
`NOT_EVALUABLE`.

Der maximal zulaessige positive Status bleibt:

```text
S2HZ_TWO_AREA_CONFLICT_SIGNAL_VALID_DIRECT_COMPARISON_EXPLAINS
```

## Auditentscheidung

S2-IA ist nach S2-IB bestanden. Der private read-only Konfliktindikator ist
statisch implementierungsfaehig.

Diese Entscheidung gibt noch keinen Code, keine Tests und keine Ausfuehrung
frei. Eine private Implementierung benoetigt eine separate ausdrueckliche
Freigabe und muss die gebundenen Formen, sechs Operationen, Ownergrenze,
Statusmatrix, Ledger und Groessenlimits unveraendert uebernehmen.

Eine automatische Kontextwahl, Memory-Erweiterung, API-, Snapshot- oder
Feldintegration bleibt weiterhin gesperrt.
