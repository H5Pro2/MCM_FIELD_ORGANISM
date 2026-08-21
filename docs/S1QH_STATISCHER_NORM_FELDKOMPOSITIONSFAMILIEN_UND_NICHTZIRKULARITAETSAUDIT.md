# S1-QH: Statischer NORM-Feldkompositionsfamilien- und Nichtzirkularitaetsaudit

## Status und Umfang

S1-QH prueft die in S1-QG offen gelassenen NORM-Feldkompositionsfamilien
`REPLACE_S`, `SCALE_S` und `SOURCE_S` gegen:

- die vorhandene W7-N-NORM-Zustands- und Outputsemantik;
- den kandidatenfreien schnellen A1-S/H-Feldpfad;
- genau eine technische Feldzeitfortschreibung;
- die S1-QA-Pflicht eines vollstaendigen signed Feldoutputs;
- Parameterfreiheit der reinen Kompositionsentscheidung;
- Nichtzirkularitaet und atomare Veroeffentlichung.

Der Audit waehlt nur eine Kompositionsfamilie. Er bindet keine neue
Differential- oder Updategleichung, keine Parameter, Werte, Toleranzen,
Schema-IDs, Implementierung, Fixture oder Runtime. Es wird kein Test und kein
Feldlauf ausgefuehrt und keine Ergebnisentscheidung getroffen.

Auditentscheidung:

```text
REPLACE_S_SELECTED_AS_ONLY_DIRECT_PARAMETER_FREE_NORM_COMPOSITION
SCALE_S_STOPPED_CHANGES_EXISTING_NORM_OUTPUT_SEMANTICS
SOURCE_S_STOPPED_REQUIRES_NEW_COUPLING_OR_SECOND_INTEGRATION
ACYCLIC_A1_PROPOSAL_NORM_STATE_FINAL_FIELD_ORDER_BOUND
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gemeinsame Zulassungskriterien

Eine Kompositionsfamilie ist nur zulaessig, wenn sie gemeinsam:

1. den vorhandenen `W7NLocalBaselineResult.output` vollstaendig und signed
   verwendet;
2. keine neue Gewichtung, Rate oder Mischkonstante benoetigt;
3. H unveraendert aus der A1-Fast-Rolle uebernimmt;
4. pro Intervall genau eine Feldzeitfortschreibung belegt;
5. keinen aktuellen Output in seine eigene aktuelle Eingabe zurueckfuehrt;
6. nur ein finales vollstaendiges Feld veroeffentlicht;
7. dieselbe Komposition in allen F/T/I/C/R/U-Armen verwendet;
8. keine Kandidaten-, Arm-, Ziel- oder Ergebnisinformation liest.

Eine Familie, die erst durch eine zusaetzliche Modellannahme eindeutig wird,
ist in S1-QH nicht zulaessig.

## Gemeinsame kausale Ausgangslage

Jedes spaetere NORM-Intervall beginnt mit:

- einem vollstaendigen gemeinsamen Feldvorzustand;
- einem vollstaendigen NORM-Privatvorzustand;
- der aktuellen modellneutralen Rezeptorverteilung;
- genau einem abgeschlossenen Feldzeitintervall;
- den unveraenderten A1- und NORM-Konfigurationsidentitaeten.

Der A1-Fast-Pfad kann aus Feldvorzustand und Rezeptorinput bereits einen
vollstaendigen kandidatenfreien Vorschlag fuer S und H ueber dieses Intervall
erzeugen. Dieser Vorschlag darf in NORM nur ein interner unveraenderlicher
Zwischenrecord sein. Er ist kein zweites veroeffentlichtes Feldresultat.

## Familie REPLACE_S

### Funktionsrolle

`REPLACE_S` verwendet den vollstaendigen signed NORM-Outputvektor unmittelbar
als finale S-Komponente desselben technischen Intervalls. Die finale
H-Komponente und alle Feld-, Geometrie-, Dock-, Perzeptions- und Zeitrollen
stammen aus dem kandidatenfreien A1-Vorschlag.

Diese Bindung ist eine Ausgabekomposition, keine neue NORM-Zustandsgleichung.
Sie verwendet weder eine Mischkonstante noch einen zusaetzlichen
Skalierungsparameter.

### Azyklische Reihenfolge

Die einzige zulaessige logische Abhaengigkeitsordnung lautet:

```text
Feldvorzustand + Rezeptorinput + Intervall
    -> interner A1-Fast-Vorschlag S_fast/H_fast
    -> NORM-Fortschreibung aus Vorzustand und vollstaendigem S_fast
    -> NORM-Folgezustand + globaler Skalierungsbeleg + signed NORM-Output
    -> finales Feld: S aus NORM-Output, H aus A1-Fast-Vorschlag
```

Das finale S darf im selben Intervall nicht erneut in den A1-Vorschlag oder
die NORM-Fortschreibung eingehen. Es wird erst zum Feldvorzustand des
naechsten Intervalls.

### Einmalige Feldzeit

Der A1-Vorschlag verbraucht die einzige technische Intervallfortschreibung.
Die abschliessende S-Ersetzung:

- veraendert keinen Tick und kein Zeitfenster;
- ruft keine Feldgleichung erneut auf;
- veraendert H, Perzeption und Rezeptorprovenienz nicht;
- wird vor jeder externen Veroeffentlichung atomar materialisiert;
- erzeugt keinen zusaetzlichen Observer- oder Reparaturschritt.

Ein intern bereits konstruiertes A1-Feld darf nicht als Teilergebnis
ausgegeben, gespeichert oder von einem Comparator gelesen werden.

### Eigene NORM-Gegenprognose

`REPLACE_S` erhaelt die in S1-QF gebundene globale Outputkopplung direkt:
Jeder finale S-Ortswert stammt aus der lokalen NORM-Koordinate unter derselben
geometrieweiten aktuellen Skalierungsgrundlage. Ein entfernter Zustand kann
dadurch den lokalen S-Output ohne Edge-Transfer skalieren.

Der A1-Vorschlag bleibt dennoch als kausale Evidence- und H-Quelle sichtbar.
Damit wird NORM weder zu einem reinen Observer noch zu einer zweiten
Feldintegration.

### REPLACE_S-Status

```text
FUNCTIONALLY_DIRECT
PARAMETER_FREE_AT_COMPOSITION_BOUNDARY
ACYCLIC_WITH_ONE_PUBLISHED_FIELD_STEP
SELECTED
```

## Familie SCALE_S

### Gepruefte Bedeutung

`SCALE_S` wuerde den A1-S-Vorschlag durch eine aus NORM abgeleitete globale
oder lokale Skalierung veraendern, statt den vorhandenen signed NORM-Output
selbst als S auszugeben.

### Methodischer Konflikt

Der vorhandene W7-N-NORM-Kern liefert bereits einen vollstaendigen signed
Outputvektor. Eine reine Skalierung des A1-Vektors muesste dagegen neu
entscheiden:

- ob nur die globale Skalierungsgroesse oder auch lokale NORM-Werte wirken;
- ob die Skalierung ortsweise oder geometrieweit erfolgt;
- wie Vorzeichen und Nullorte des NORM-Outputs behandelt werden;
- ob A1-S multipliziert, begrenzt oder anderweitig transformiert wird.

Keine dieser Entscheidungen ist im vorhandenen NORM-Kern gebunden. Die
Familie wuerde dessen Outputsemantik veraendern oder nur einen Teiloutput
verwenden. Sie koennte zudem ohne klare Grenze in einen zustandsbehafteten
Gainarm uebergehen.

### SCALE_S-Status

```text
EXISTING_NORM_OUTPUT_NOT_USED_DIRECTLY
NEW_FIELD_TRANSFORM_SEMANTICS_REQUIRED
STOPPED
```

SCALE_S wird nicht als Parallelarm, Ablation oder spaetere
Parametersensitivitaet beibehalten.

## Familie SOURCE_S

### Gepruefte Bedeutung

`SOURCE_S` wuerde den NORM-Output als zusaetzliche Quelle innerhalb der
gemeinsamen S-Feldfortschreibung behandeln.

### Methodischer Konflikt

Eine Quellrolle benoetigt mindestens eine neue Entscheidung ueber:

- Einwirkungsstaerke oder Einheitenbezug;
- additive, begrenzende oder ersetzende Quellenwirkung;
- Einwirkungszeitpunkt innerhalb des Intervalls;
- gemeinsame Integration mit S und H;
- Rueckwirkung des entstehenden S auf den aktuellen NORM-Zustand.

Wird NORM zuerst aus dem aktuellen A1-S fortgeschrieben und danach als Quelle
in dasselbe Intervall eingespeist, entsteht eine zirkulaere Abhaengigkeit oder
eine zweite Integration. Wird nur der alte NORM-Zustand als Quelle verwendet,
entsteht eine neue explizite Ein-Intervall-Latenz, die nicht zum vorhandenen
NORM-Outputvertrag gehoert.

### SOURCE_S-Status

```text
NEW_COUPLING_AND_TIMING_RULE_REQUIRED
CURRENT_INTERVAL_DEPENDENCY_CIRCULAR_OR_DELAYED
STOPPED
```

SOURCE_S wird nicht als Kandidatenfunktion oder spaetere NORM-Variante
offengehalten.

## Vergleichsmatrix

| Kriterium | REPLACE_S | SCALE_S | SOURCE_S |
|---|---|---|---|
| vorhandener signed NORM-Output direkt genutzt | ja | nein | nur als Quelle |
| neue Misch- oder Kopplungsregel erforderlich | nein | ja | ja |
| genau eine Feldzeitfortschreibung moeglich | ja | ja, aber semantisch neu | nicht ohne neue Zeitregel |
| A1-H unveraendert uebernehmbar | ja | formal ja | nur mit neuer Kopplung |
| aktuelle Abhaengigkeitsordnung azyklisch | ja | ja | nein oder zusaetzlich verzoegert |
| S1-QF-Gegenprognose direkt erhalten | ja | unbestimmt | veraendert |
| Entscheidung | weiter | Stopp | Stopp |

## Verbindliche REPLACE_S-Datengrenzen

Der spaetere atomare Kompositor darf ausschliesslich erhalten:

- vollstaendigen Feldvorzustand;
- vollstaendigen NORM-Vorstatus;
- aktuelle Rezeptorverteilung und Intervallzeit;
- unveraenderte A1- und NORM-Konfigurationen;
- intern erzeugten vollstaendigen A1-Vorschlag;
- vollstaendigen NORM-Folgezustand, Skalierungsrecord und signed Output.

Er darf nicht erhalten:

- Expositionsfamilie, Armname oder erwartete Richtung;
- Kandidatenzustand oder Kandidatenbilanz;
- Comparatorresultat oder Zielvektor;
- historischen W7-P-Observertrace;
- ausgewaehlte Knoten oder nachtraegliche Skalare;
- einen zweiten Feldzeit- oder Integrationsauftrag.

## Feldidentitaet und Materialisierung

Das finale REPLACE_S-Feld muss gegen den internen A1-Vorschlag bitgleich
erhalten:

- Feld-, Schicht- und Geometrieidentitaet;
- Knoten- und Dockordnung;
- Knotenpositionen und Modalitaetsrollen;
- Tick, Perzeption und letzte Rezeptorverteilung;
- H an jedem Knoten;
- Abwesenheit eines Kandidaten-, Substrat- oder Entwicklungszustands.

Abweichen darf ausschliesslich die vollstaendige S-Komponente, die exakt dem
signed NORM-Outputvektor in derselben Knotenordnung entsprechen muss.

Ein finales Feld mit Nullsubstratobjekt, zusaetzlichem Entwicklungspayload
oder historischem Profilzustand ist unzulaessig.

## Frischstart und Carry

REPLACE_S startet pro Arm aus:

- demselben neutralen gemeinsamen Frischfeld wie A1;
- einem unabhaengigen NORM-Frischzustand derselben Geometrie;
- unveraenderten A1- und NORM-Konfigurationsidentitaeten.

Nach einem gueltigen Intervall werden gemeinsam getragen:

- das finale REPLACE_S-Feld als naechster Feldvorzustand;
- der vollstaendige NORM-Folgezustand als naechster Privatvorzustand.

Der interne A1-Vorschlag, Skalierungsrecord und NORM-Outputvektor bleiben
Outputprovenienz desselben Intervalls, aber keine zusaetzlichen
Carryzustaende.

## Atomare Ausgabe

Ein spaeterer REPLACE_S-Kompositor muss atomar liefern:

- S1-QD-Eingabe- und Frischprovenienz;
- Digest des Feld- und NORM-Vorzustands;
- vollstaendigen internen A1-Vorschlagsdigest;
- vollstaendigen NORM-Folgezustand;
- Skalierungsrecord und signed NORM-Outputdigest;
- finales vollstaendiges S/H-Feld;
- Beleg der S-Ersetzung und H-Identitaet;
- Beleg genau einer Feldzeitfortschreibung;
- technische Diagnostik und Gesamtdigest;
- genau einen Abschlussstatus.

Kein Zwischenrecord darf separat als Feldresultat gelten.

## Fail-Closed-Regeln

REPLACE_S bleibt `NOT_COMPUTABLE`, wenn:

- A1-Vorschlag und NORM-Evidence nicht dasselbe Intervall binden;
- NORM-Output und finales S nicht exakt dieselbe Knotenordnung besitzen;
- irgendeine finale S-Komponente nicht aus dem NORM-Output stammt;
- H oder andere Feldrollen gegen den A1-Vorschlag veraendert werden;
- das finale Feld einen zweiten Tick oder ein zweites Zeitfenster traegt;
- das finale S in die aktuelle NORM-Fortschreibung zurueckgefuehrt wird;
- der interne A1-Vorschlag vor atomarem Abschluss sichtbar wird;
- ein Mischgewicht, Gain oder armweise Kompositionswahl erscheint;
- SCALE_S oder SOURCE_S still als Teilpfad hinzukommt;
- ein Substrat-, Entwicklungs- oder Kandidatenzustand getragen wird;
- ein Teiloutput nach einem Fehler veroeffentlicht wird.

Ein Kompositionsfehler erzeugt kein Kandidatenresiduum.

## Bestands- und Implementierungsgrenze

Vorhanden und wiederverwendbar sind:

- der kandidatenfreie A1-Fast-Feldpfad;
- der W7-N-NORM-Frischzustand und Intervallkern;
- der vollstaendige signed NORM-Output;
- die immutable Feld-, Knoten- und Digestoberflaechen.

Noch nicht vorhanden ist der private atomare REPLACE_S-Kompositor samt
S1-QD-Huelle, Provenienzrecord und Fail-Closed-Ausgabe.

Status:

```text
REPLACE_S_COMPOSITION_FAMILY_BOUND
ATOMIC_COMPOSITOR_IMPLEMENTATION_STILL_MISSING
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

## Aussagegrenze

S1-QH waehlt nur die kleinste konsistente Feldkompositionsfamilie fuer eine
technische Gegenbaseline. Es gibt keine neue Feldgleichung, keine Parameter,
keine Implementierung, keinen Feldlauf, keinen Kandidaten und keinen Befund zu
einer hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QI - statischer A3-NORM-REPLACE_S-Kompositor-, Fehlercode- und
        Testbudgetvertrag
```

S1-QI soll ausschliesslich Modulgrenze, Eingabe- und Ausgabeschemata,
atomare Materialisierung, kanonische Digests, endliche Fehlercodes und ein
kleines technisches Testbudget fuer den privaten REPLACE_S-Kompositor binden.
Noch keine Implementierung, Fixturewerte, Testausfuehrung, Runtimeintegration,
Lebenszyklusausfuehrung oder Ergebnisentscheidung.
