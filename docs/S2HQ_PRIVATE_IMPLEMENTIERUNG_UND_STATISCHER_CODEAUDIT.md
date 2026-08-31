# S2-HQ: Private Implementierung und statischer Codeaudit

Status: `PRIVATE_IMPLEMENTATION_STATIC_AUDIT_PASS_TESTS_LOCKED`

## Umfang

S2-HQ implementiert ausschliesslich drei neue private Module:

1. `_s2hq_private_byte_block_conflict_fixture.py`;
2. `_s2hq_private_role_addressed_context_consumer.py`;
3. `_s2hq_private_direct_role_addressed_mask_fill_baseline.py`.

Es wurden keine Tests angelegt oder ausgefuehrt, keine neuen Module importiert,
keine Bilder materialisiert und keine Rezeptor-, Speicher-, Projektions- oder
Verbrauchsfunktion aufgerufen. Der Audit bestand aus Syntax-, AST-, Quellen-,
Import- und Digestpruefungen.

Die bestehende binaere S2-GT-Registry, S2-GK, S2-GC, S2-GI, B4, TSPM-1,
PPB-1, API, Snapshot und Feldpfad bleiben unveraendert.

## 1. Private Byte-Block-Fixture

Das Fixturemodul bindet:

- vier visuelle Byte-Block-Fixtures V0, V1, Q0 und Q1;
- exakt 18 ganzzahlige Blockwerte je Fixture im Bereich `0..255`;
- die feste Bildform `80 x 120 x 3`;
- die feste Rasterform `2 x 3 x 3` und Blockform `40 x 40`;
- den SHA-256-Digest der vollstaendig expandierten Bildbytes;
- drei getrennt als synthetisch gekennzeichnete auditive Rezeptorzustaende
  M0, M1 und MQ;
- zwei spiegelbildliche Richtungen und vier neutrale Rollenfaelle.

Die Bildmaterialisierung ist eine ausdruecklich aufzurufende reine Funktion.
Sie erzeugt ein `uint8`-Array, prueft Form und Rohbilddigest und markiert das
Ergebnis read-only. Es gibt keine Importzeit-Ausfuehrung des Rezeptors und
keine Dateioperation.

Fallkennungen und erwartete visuelle Werte liegen getrennt in
Evaluationsmetadaten. Weder Verbraucher noch Direktbaseline importieren das
Fixturemodul. Dadurch koennen Sollwerte und Fallrollen nicht in die
Funktionsentscheidung gelangen.

## 2. Rollenadressierter Verbraucher

`RoleAddressedContextUseBinding` bindet genau:

- maskierte Probe und Probequelle;
- validiertes S2-GI-Bundle und Bundlequelle;
- Composite-Zustand;
- ausdruecklich gewaehltes `A_RECENT` oder `B_STABLE`;
- Findingdigest des gewaehlt adressierten Bereichs.

Andere Rollenwerte werden bereits beim Aufbau und erneut beim Verbrauch
fail-closed abgewiesen. Es existieren kein Feld fuer eine Rangfolge, kein
`BEST_MEMORY`, keine automatische Auswahl und keine Ausweichrolle.

Die Wertquellen sind fest im Code getrennt:

```text
A_RECENT -> area_findings[0].recent_content
          -> B4_RECENT
          -> genau eine AV_JOINT-Komponente
          -> visuelle Werte 8..25

B_STABLE -> area_findings[1].stable_content
          -> TSPM_SLOW
          -> genau eine stabile VISUAL-Komponente
          -> 18 visuelle Werte
```

`A_RECENT.fast_internal` wird bei der Bundleabnahme validiert, aber nie als
Wertquelle oder Fallback verwendet. Ein fehlender Kandidat, eine falsche
Rolle, eine mehrdeutige Komponente oder eine ungueltige Stabilitaetsbindung
stoppt vor jeder Ausgabe.

Der Verbraucher vergleicht ausschliesslich die neun sichtbaren Positionen.
Bei Uebereinstimmung werden genau die neun maskierten Positionen gefuellt.
Bei sichtbarem Konflikt bleibt die gesamte Maske leer. Teilfuellung ist durch
die Ergebnisform ausgeschlossen.

Vor und nach dem Verbrauch werden Bundle-, Vorzustands- und
Nachzustandsdigest verglichen. Der Verbraucher besitzt keine Speicher- oder
Projektionsfunktion und kann den Zustand nicht fortschreiben.

## 3. Unabhaengige Direktbaseline

Die Direktbaseline besitzt eigene:

- Fehlercodes;
- Bundle- und Rollenvalidierung;
- A- und B-Komponentenauslesung;
- Maskenfuellung;
- Ledger- und Ergebnisformen;
- Digestbildung.

Sie ruft `complete_from_explicit_area` nicht auf und uebernimmt kein
Verbraucherergebnis. Sie verwendet lediglich die gemeinsamen privaten
Datentypen und die identische Rollenbindung, damit beide Arme denselben
Eingang erhalten.

Verbraucher und Baseline zaehlen fuer beide Rollen jeweils:

- 18 Maskenvalidierungen;
- neun sichtbare Vergleiche;
- null oder neun Maskenkopien;
- genau einen Bereichslookup;
- genau eine Kandidaten- und Komponentenreferenz;
- 18 Wertreferenzen;
- zwei Digestoperationen.

Die Funktionsbudgets sind damit rollen- und armgleich. Unterschiedliche
interne Anatomie von A und B wird nicht als kostenloser Vorteil gewertet.

## 4. Nicht gewaehlter Bereich

Das vollstaendige S2-GI-Bundle wird vor dem Verbrauch validiert und als
Provenienz gebunden. Danach wird funktional nur der ausdruecklich gewaehlte
Bereich gelesen.

Der nicht gewaehlte Kandidat kann daher den Ausgabewert, den Status, die Zahl
kopierter Werte oder das Funktionsbudget nicht beeinflussen. Sein Anteil am
Bundle-Digest bleibt als Herkunftsbindung sichtbar. Ein beschaedigtes Bundle
wird insgesamt fail-closed abgewiesen und erzeugt kein Teilergebnis.

## 5. Statische Auditbelege

Die drei Dateien wurden als Python-AST ohne Modulimport geparst. Festgestellt
wurden:

- keine Syntaxfehler;
- vier visuelle und drei auditive Fixtures;
- zwei Richtungen und vier Rollenfaelle;
- keine Aufrufe von PPB-, TSPM-, Composite-Probe- oder Feldfunktionen;
- kein Aufruf des Verbrauchers durch die Direktbaseline;
- keine Imports von S2-GT-Runner, API, Snapshot oder Feldpfad;
- keine Importe der Evaluationsfixture durch Verbraucher oder Baseline;
- keine automatische Auswahl oder Ergebnisverschmelzung;
- keine Aenderung einer bestehenden Datei.

Quellhashes nach der Implementierung:

| Datei | SHA-256 |
|---|---|
| Byte-Block-Fixture | `6b5adce16f7b3523f4a521636d4687b07b7728c2986ff070f1692524e23a3898` |
| Rollenverbraucher | `cb9b3ecea1bfd0090d379bdbd46c317565ea58d664d2b3f66a64f33008960e57` |
| Direktbaseline | `e42ed48b7c06baf5939654be0e470e8d39e8e98e837680c6128c92ac46c12254` |

Der unveraenderte S2-GT-Fixtureregister besitzt weiterhin den Digest:

```text
5d4ed450c2443f51839acfb9717661b8c54422be3fd87605c50b020e5a887849
```

## 6. Entscheidung und naechster Schritt

Die private Implementierung besteht den statischen Codeaudit. Sie erzeugt
noch keinen Funktionsbefund.

Weiterhin gesperrt sind:

- Tests und Qualifikationsaufrufe;
- Ausfuehrung der vier Rollenfaelle;
- Bildung der beiden Speicherhistorien;
- Runner und Ergebnisablage;
- Feldintegration, API und Snapshot;
- automatische Kontextwahl.

Der naechste zulaessige Schritt ist eine getrennt freizugebende neutrale
Qualifikation. Sie muss Byte-Block-Anatomie, explizite Rollenisolierung,
unabhaengige Baseline, Fail-Closed-Grenzen und read-only Unveraendertheit
pruefen, ohne die spaeteren Bildungsgeschichten auszufuehren.
