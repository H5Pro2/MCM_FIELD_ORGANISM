# S1-NY G2/D3 Audit minimaler lokaler Bildungsmechanismusklassen

## Status

S1-NY auditiert minimale Mechanismusklassen gegen den S1-NX-F2-Vertrag und
fuehrt hoechstens eine Klasse weiter. Der Schritt bindet keine
Bildungsgleichung, keinen Betrag, keine Rate, keinen Parameter, keine Runtime
und keine Feldwirkung und fuehrt nichts aus.

Entscheidung:

```text
SELECT_G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION_CLASS_ONLY
```

## Auditkriterien

Eine weiterfuehrbare Klasse muss gleichzeitig:

1. H0 gegen H1 und Spiegelarm allein aus lokaler Kontaktordnung trennen;
2. bei gleicher Kontaktmenge, Dosis und Orientierungsbilanz arbeiten;
3. X-Fortsetzung und Y-Fortsetzung gleich behandeln;
4. ausschliesslich `bound_unconfigured -> bound_configured` umordnen;
5. Kapazitaet und aggregiertes `free/bound/blocked` exakt erhalten;
6. ohne Arm-ID, Lookup, Reward, Zielwert oder Ergebniswissen auskommen;
7. keine Vierkontaktfolge, Ereignisliste oder Rohdaten speichern;
8. kleiner als ein neuer Integrator-, Netzwerk- oder Replayzustand bleiben;
9. spaetere Abschwaechung, Interferenz und Loesung prinzipiell offenlassen;
10. gegen Fixed Adapter, Leaky, Integrator, DTS-1 und T1 falsifizierbar
    bleiben.

Eine Klasse wird nicht deshalb eigenstaendig, weil sie einen neuen Namen
erhaelt.

## F0: Kontaktzaehler oder Dosisakkumulator

F0 bildet nur Kontaktzahl oder aufsummierte Beteiligung ab.

H0, H1 und Spiegelarm besitzen jeweils vier Kontakte, zweimal X, zweimal Y
und dieselbe Beteiligungsdosis. F0 muss deshalb in allen Armen bitgleich sein
und kann die F2-Prognose nicht tragen.

```text
STOP_F0_EQUAL_DOSE_ACCUMULATOR_HAS_NO_ORDER_AXIS
```

## F1: letzter Kontakt oder feste Orientierung

F1 bildet nur die letzte Orientierung oder bevorzugt X beziehungsweise Y.

H0 und H1 enden beide mit Y; der Spiegelarm endet mit X. Ein Endkontaktadapter
kann daher H0 und H1 nicht trennen oder verletzt die Spiegelkontrolle.

```text
STOP_F1_TERMINAL_ORIENTATION_IS_LABEL_ADAPTER
```

## F2: unabhaengiger Leaky- oder Integratorskalar

F2 fuehrt einen neuen lokalen Skalar ein, der Kontaktwerte leaky oder
integrativ sammelt und danach eine D3-Umordnung steuert.

Eine solche Klasse kann Ordnungseffekte erzeugen, ist aber ohne weitere
Ressourcenbindung bereits genau die vorregistrierte Leaky-/Integratorerklaerung
in neuer Benennung. Der vorhandene D3-Zustand begrenzt den Ausgang, begruendet
aber keinen zweiten ungebundenen Akkumulator.

```text
STOP_F2_INDEPENDENT_TRACE_IS_REGISTERED_BASELINE
```

## F3: transiente lokale Fortsetzungspruefung

F3 vergleicht an einer atomaren lokalen Intervallgrenze nur den unmittelbar
abgeschlossenen Kontakt mit dem aktuellen Kontakt. Das Ergebnisalphabet ist
vorlaeufig:

```text
NO_PREDECESSOR
LOCAL_CONTINUATION
LOCAL_SWITCH
```

Dabei gilt auf Klassenebene:

```text
X -> X = LOCAL_CONTINUATION
Y -> Y = LOCAL_CONTINUATION
X -> Y = LOCAL_SWITCH
Y -> X = LOCAL_SWITCH
```

Die Klassifikation wird transient am Zweiintervallrand gebildet und nach der
lokalen Commitgrenze verworfen. Sie darf keinen Kontaktwert, keine Folge und
keinen Zaehler in D3 speichern.

Nur `LOCAL_CONTINUATION` darf eine spaetere konservative Umordnung innerhalb
des bereits gebundenen `bound` zulassen. `NO_PREDECESSOR` und `LOCAL_SWITCH`
haben fuer Bildung die Nullprognose. Betrag und Regel dieser Umordnung bleiben
in S1-NY offen.

Fuer die drei S1-NX-Geschichten folgt das reine Ereignismuster:

```text
H0_ALTERNATING = SWITCH, SWITCH, SWITCH
H1_GROUPED     = CONTINUATION, SWITCH, CONTINUATION
H1_MIRRORED    = CONTINUATION, SWITCH, CONTINUATION
```

Damit ist die Klasse ordnungssensitiv, dosisgleich und gespiegelt. Sie
benoetigt keinen Vierkontaktpuffer und keine feste Orientierung.

```text
PASS_F3_TO_TRANSIENT_EVENT_ANATOMY_AND_CONSERVATION_CONTRACT
```

F3 wird als einzige Klasse weitergefuehrt.

## F4: Kontaktfolge, Replay oder Ereignisindex

F4 speichert die vier Kontakte, ihre Armkennung oder einen fortlaufenden
Sequenzindex und entscheidet danach H0 gegen H1.

Damit wuerde die erwartete Geschichte direkt wiedererkannt statt durch lokale
Ressourcenumordnung wirksam zu werden.

```text
STOP_F4_SEQUENCE_BUFFER_OR_REPLAY_FORBIDDEN
```

## F5: Mehrkanten- oder globale Musterklasse

F5 vergleicht Nachbarkanten, globale Feldmuster oder mehrere Traegergruppen.

Der F2-Vertrag besitzt genau eine Kante und zwei lokale Orientierungen. Eine
globale oder relationale Erweiterung waere nicht beobachtbar und fuer die
aktuelle Falsifikation unnoetig.

```text
STOP_F5_NONLOCAL_STRUCTURE_PREMATURE_FOR_F2
```

## Ausgewaehlte Klasse

Weitergefuehrt wird ausschliesslich:

```text
G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION
```

Die Klasse besitzt genau zwei getrennte Rollen:

- ein transientes, nicht persistiertes Ereignis an einer lokalen
  Zweiintervallgrenze;
- die bereits vorhandene persistierbare D3-Unterteilung als konservatives
  Ziel einer spaeteren Umordnung.

Nicht Teil der Klasse sind:

- ein neuer frei laufender Skalar;
- eine Kontaktliste oder Arm-ID;
- eine feste X-/Y-Bevorzugung;
- ein globales Muster oder Mehrkantenzustand;
- eine Umordnungsmenge, Rate oder Schwelle;
- Abschwaechungs-, Interferenz- oder Loesungsregeln.

## Konservative Ressourcengrenze

Eine spaetere F3-Bildung darf nur innerhalb derselben Kante wirken:

```text
bound_unconfigured decreases
bound_configured increases by the same amount

free unchanged
blocked unchanged
capacity unchanged
aggregate bound unchanged
```

Ohne positive `bound_unconfigured`-Ressource ist keine Bildung zulaessig. Es
gibt keine Reserve, negative Rolle oder globale Ausgleichsbuchung.

## Abgrenzung zu den Baselines

### Fixed Adapter

Ein zustandsloser Adapter des aktuellen Kontakts kann den unmittelbaren
Vorgaenger nicht unterscheiden. Ein neu eingefuehrter zustandsbehafteter
Adapter mit demselben Vorgaengervergleich waere dagegen eine faire
Gegenerklaerung und muss spaeter explizit registriert werden. Reproduziert er
den gesamten Lebenszyklus, wird F3 verworfen und nicht nur umbenannt.

### Leaky und Integrator

Leaky- und Integratorarme sehen dieselben vollstaendigen Geschichten. F3 ist
nicht allein deshalb eigenstaendig, weil sein Ereignisalphabet diskret ist.
Koennen ihre vorregistrierten Zustaende Bildung, Spaetwirkung,
Abschwaechung, Interferenz und Loesung vollstaendig reproduzieren, wird F3
gestoppt.

### DTS-1 und geschaltetes T1

Beide duerfen dieselbe transiente Ereignisinformation als Kontrolle sehen,
besitzen aber keine D3-Unterteilung. Veraendern sie fuer H0 und H1 das
aggregierte Ledger verschieden, verletzt dies die F2-Angleichungsgrenze und
ist keine G2-Bildung.

### Replay und Lookup

Ein gespeicherter Vorgaenger ueber die atomare Vergleichsgrenze hinaus, eine
Viererfolge oder eine H0/H1-Tabelle sind unzulaessig. Der transiente
Zweiintervallvergleich darf nach Commit nicht lesbar bleiben.

## Verwerfungsbedingungen

F3 wird vor Implementierung verworfen, wenn:

- die lokale Fortsetzung nicht ohne Folgepuffer klassifizierbar ist;
- X- und Y-Fortsetzung unterschiedliche Bildungsrollen benoetigen;
- ein Switch oder erster Kontakt positive Bildung ausloesen muss;
- eine zusaetzliche ungebundene Akkumulatorvariable erforderlich ist;
- die Umordnung aggregiertes `bound`, `free`, `blocked` oder Kapazitaet
  veraendert;
- die Ereignisrolle nach Commit persistiert;
- ein zustandsbehafteter Adapter bereits auf Vertragsniveau dieselbe
  vollstaendige Funktionsprognose traegt;
- Abschwaechung, Interferenz oder Loesung prinzipiell eine gespeicherte
  Kontaktfolge erfordern.

## Aussagegrenze

S1-NY waehlt nur eine minimale Bildungsmechanismusklasse. Eine transiente
Fortsetzungspruefung ist noch keine Bildungsgleichung und kein Befund, dass
das MCM-Feld eine solche Umordnung hervorbringt. Es gibt keine Bildung,
Spaetwirkung, Abschwaechung, Interferenz, Loesung oder Feldwirkung, keine
Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NZ darf ausschliesslich die transiente lokale Zweiintervallanatomie, das
endliche Ereignisalphabet, die Commit- und Verwerfungsgrenze sowie die
konservative D3-Zielprojektion statisch binden. Es muss insbesondere zeigen,
dass nach Commit kein Vorgaenger- oder Sequenzzustand verbleibt.

S1-NZ darf noch keine Umordnungsmenge, Rate, Schwelle, Bildungsgleichung,
Runtime, Transferbuchung oder Feldwirkung implementieren oder ausfuehren.
