# S1-QB: Statischer Pflichtbaseline-Oberflaechen- und Informationsaudit

## Status und Umfang

S1-QB prueft jede durch S1-PX geforderte einfachere Erklaerung gegen die
S1-PZ-Lebenszyklusgeschichten und die S1-QA-Beobachtungsoberflaeche. Der Audit
bewertet ausschliesslich vorhandene unveraenderte Kerne, oeffentliche oder
private Aufrufgrenzen und notwendige Informationssperren.

S1-QB implementiert keinen Adapter, keine Baseline und keinen Comparator. Es
werden keine Gleichung, Parameter, Werte, Toleranzen, Digests oder Fixture
neu gebunden. Kein Test und kein Feldlauf wurden ausgefuehrt.

Auditentscheidung:

```text
EXISTING_BASELINE_KERNELS_PARTIALLY_REUSABLE
MANDATORY_S1PX_LIFECYCLE_BASELINE_SURFACE_INCOMPLETE
MISSING_DISTINCT_BASELINE_ROLES_REQUIRE_STATIC_CONTRACTS_BEFORE_IMPLEMENTATION
```

## Zulassungskriterium

Eine Baseline gilt in S1-QB nur dann als oberflaechenfaehig, wenn ein
vorhandener unveraenderter Kern spaeter:

- alle F/T/I/C/R/U-Geschichten in derselben Kausalreihenfolge aufnehmen kann;
- aus einem eigenen registrierten Frischzustand startet;
- seinen vollstaendigen privaten Zustand nur innerhalb einer Replik traegt;
- genau eine Konfigurationsidentitaet ueber alle Arme verwendet;
- S/H-Angleichung ohne privaten Zustandsverlust uebersteht;
- nach jeder Probe eine vollstaendige signed S-Fortsetzung liefern kann;
- atomar und fail-closed ausgibt;
- weder Armwissen noch Kandidatenzustand, Zielwerte oder Zukunftsdaten liest.

Ein vorhandener Skalarrechner, Probehelfer oder historischer Falloutput ist
noch keine zugelassene Lebenszyklusbaseline.

## Statusklassen

S1-QB verwendet vier statische Klassen:

| Klasse | Bedeutung |
|---|---|
| `INTERVAL_CORE_PRESENT_NEW_ENVELOPE_BINDING_REQUIRED` | Vollstaendiger Feldintervallkern und private Zustandsfuehrung sind vorhanden; die neue S1-PZ-Huelle fehlt. |
| `KERNEL_PRESENT_FUNCTIONAL_HANDOFF_UNBOUND` | Ein passender Rechenkern existiert, liefert aber noch kein vollstaendiges S1-QA-Feldresultat. |
| `SPECIALIZED_CLOSED_SURFACE_NOT_DIRECTLY_ADMISSIBLE` | Bestand ist an alte Ereignisse, Sidecars, Checkpoints oder geschlossene Kandidaten gebunden. |
| `NO_ADMISSIBLE_CORE_PRESENT` | Im Projekt existiert kein eigenstaendiger unveraenderter Kern fuer die Pflichtrolle. |

Keine dieser Klassen ist eine Ausfuehrungsfreigabe.

## A - Aktueller Rezeptorkontakt

Vorhandener Kern:

```text
mcm_field_organism/carrier_baselines.py
stateless_baseline(contact)
```

Der Kern gibt aktuellen Kontakt direkt als Aktivierung aus und fuehrt keinen
Nachhall. Er ist als zustandslose Gegenrolle fachlich passend, arbeitet aber
auf `CarrierFrame` statt auf der gemeinsamen Feld- und Resultatoberflaeche.

Klassifikation:

```text
KERNEL_PRESENT_FUNCTIONAL_HANDOFF_UNBOUND
```

Erforderlich waere spaeter ein reiner privater Handoff, der denselben
Rezeptorkontakt, dieselbe Geometrie und dieselbe Probe in ein vollstaendiges
S1-QA-Feldresultat ueberfuehrt. Der Handoff darf keine Geschichte speichern.

## B - Schneller Nachhall H und feste Zeitskalen

### Einzelner schneller Nachhall

Der aktive Feldkern besitzt mit
`advance_neutral_fast_shared_field` und seiner transienten Variante eine
vollstaendige S/H-Feldoberflaeche. Er ist als kandidatenfreier Nullpfad mit
einem festen H-Zeitparameter technisch verwendbar.

Klassifikation:

```text
INTERVAL_CORE_PRESENT_NEW_ENVELOPE_BINDING_REQUIRED
```

Der Kern bleibt aktiver Feldkern und wird nicht zu einem neuen Kandidaten. Ein
spaeterer Baselinewrapper muss nur den Kandidaten deaktivieren und den
unveraenderten schnellen S/H-Pfad durch alle Geschichten tragen.

### Mehrere feste Zeitskalen

`carrier_baselines.py` und W7-N koennen einzelne leaky Zustaende tragen. Im
Bestand existiert jedoch kein allgemein angebundener Mehrzeitskalenkern, der
mehrere feste Spuren gemeinsam durch F/T/I/C/R/U traegt und eine einzige
vollstaendige S-Fortsetzung liefert.

Klassifikation:

```text
NO_ADMISSIBLE_CORE_PRESENT
```

Mehrere separat passend gewaehlte Leaky-Arme duerfen diese Rolle nicht
ersetzen, weil dies eine armweise Modellwahl waere.

## C - Fixed Adapter, Frozen-E1 und permanentes Gewicht

Der B1-Pfad in
`dynamic_substrate_dts1_private_baseline_adapters.py` fuehrt einen vor der
Armdivergenz fixierten Adapter als unveraenderten privaten Zustand und liefert
ein vollstaendiges Feldresultat. S1-HG hat Frozen-E1 gegen diese Erklaerung
geschlossen. Ein permanentes Gewicht ist funktional dieselbe statische
Kopplungsklasse und benoetigt keinen absichtlich duplizierten Modellarm.

Klassifikation:

```text
INTERVAL_CORE_PRESENT_NEW_ENVELOPE_BINDING_REQUIRED
```

Wiederverwendet werden darf nur der unveraenderte Fixed-Adapter-Kern. Alte
Frozen-E1-Runner, Receipts und Feldvektoren bleiben geschlossen.

## D - Leaky und Integrator

Die bestehenden privaten B2- und B3-Pfade decken ab:

- B2: lineare S2-Integratorbaseline mit vollstaendigem L-Zustand;
- B3: lokale F3-Leaky-Baseline mit vollstaendigem M-Zustand.

Beide Kerne sind fuer Zwei- und Dreiknotengeometrien technisch abgenommen und
geben vollstaendige Felder sowie private Folgezustaende atomar zurueck.

Klassifikation:

```text
INTERVAL_CORE_PRESENT_NEW_ENVELOPE_BINDING_REQUIRED
```

Die bisherigen P_IE/P_IH/P_IK/P_IN-Profile werden nicht uebernommen. Nur die
Intervallkerne und privaten Zustandsgrenzen sind wiederverwendbar.

## E - Lineare, volle und CONST-V-Feldgegenrollen

Die privaten B4-, B5- und B6-Pfade stellen zusaetzliche starke Gegenrollen
bereit:

- linear gekoppelte F3-Baseline;
- vollstaendige F3-Baseline;
- eingefrorene CONST-V-Baseline.

Sie ersetzen keine fehlende Pflichtrolle, bleiben aber im spaeteren
Gesamtvergleich zulaessige Zusatzbaselines.

Klassifikation:

```text
INTERVAL_CORE_PRESENT_NEW_ENVELOPE_BINDING_REQUIRED
```

Auch hier darf nur ein neuer S1-PZ-Huellenadapter hinzukommen; Gleichungen und
interne Zustaende bleiben unveraendert.

## F - Feste Verzoegerung

`auditory_field_function_probe.py` enthaelt eine feste
Ein-Schritt-Verzoegerung nur als lokales Vergleichskriterium eines
spezialisierten Auditlaufs. Es existiert kein eigenstaendiger Baselinekern mit
privatem Delayzustand, gemeinsamer Feldoberflaeche und F/T/I/C/R/U-Carry.

Klassifikation:

```text
NO_ADMISSIBLE_CORE_PRESENT
```

Der alte boolesche Probevergleich ist kein Formadapter und darf nicht als
Lebenszyklusbaseline ausgegeben werden.

## G - Statische Rekurrenz

`condensed_field_form_null_probe.py` besitzt mit `_recurrent_history` einen
privaten, probespezifischen Hilfsrechner. Er ist weder eine oeffentliche
Modelloberflaeche noch an gemeinsame Feldgeometrie, Frischzustand,
Konfigurationsdigest oder S1-QA-Output gebunden.

Klassifikation:

```text
NO_ADMISSIBLE_CORE_PRESENT
```

Die lineare B4-Feldgegenrolle bleibt eine zusaetzliche dynamische Baseline,
ist aber nicht automatisch mit einer reinen statischen Rekurrenz identisch.

## H - Replay oder gespeicherte Eingabefolge

Im aktiven oder als Baseline klassifizierten Projektbestand existiert kein
Replaykern. Vorhandene Replaybezeichnungen sind Sperren oder historische
Vergleichserwaehnungen, keine ausfuehrbare private Baselineoberflaeche.

Klassifikation:

```text
NO_ADMISSIBLE_CORE_PRESENT
```

Replay bleibt als Kandidatenabkuerzung verboten. Als spaetere negative
Gegenbaseline duerfte es nur nach einem eigenen statischen Vertrag entstehen,
der gespeicherte Eingaben strikt im privaten Baselinezustand haelt und sie
niemals dem Kandidaten oder Feldkern als versteckte Eingabe zufuehrt.

## I - Saettigung und globale Normalisierung

`w7n_capacity_function_baselines.py` besitzt eingefrorene lokale Kerne fuer:

- leaky Zustand;
- saturierenden Zustand;
- normalisierten Observeroutput.

Die Kerne fuehren einen vollstaendigen privaten Skalarzustand pro Ort, liefern
aber `W7NLocalBaselineResult` statt eines vollstaendigen gemeinsamen
S-Feldresultats. Insbesondere ist der Normalisierungsausgang dort
Observeroutput und noch keine Feldfortsetzung.

Klassifikation:

```text
KERNEL_PRESENT_FUNCTIONAL_HANDOFF_UNBOUND
```

Ein spaeterer Vertrag muss zuerst entscheiden, wie der bestehende Output ohne
neue Dynamik auf die S1-QA-Feldoberflaeche abgebildet werden kann. Ist dafuer
eine neue Rueckwirkungsgleichung erforderlich, ist der vorhandene Kern nicht
unveraendert anschliessbar und die Baseline bleibt gesperrt.

## J - Capacity-Clamp

S1-PO bindet die minimale statische Regel, nach der ein letzter Commit nur von
Angebot und aktuell freier Menge begrenzt wird. Diese Regel besitzt keinen
eigenen F/T/I/C/R/U-Zustands- und Feldpfad.

Die vorhandene kapazitaetsbegrenzte F3-Runtime ist keine reine
Capacity-Clamp-Gegenbaseline: Sie fuehrt eine eigene M-Dynamik, lokale
Vacancyfaktoren und Feldkopplung. Sie darf den fehlenden minimalen Clamp nicht
ersetzen.

Klassifikation:

```text
NO_ADMISSIBLE_CORE_PRESENT
```

Der spaetere Clamp muss dieselbe aeussere Geschichte sehen, darf aber nur
seinen eigenen aktuellen Angebots- und Kapazitaetszustand verwenden. Er darf
keinen Kandidatenledger lesen.

## K - DTS-1 und T1 als geschlossene Dreirollenbaseline

Fuer DTS-1 existieren ein gekoppelter S/H-Feldschritt, Ressourcenledger,
Backreaction und technische Auditpfade. T1 besitzt einen reinen lokalen
`free/bound/blocked`-Kantenschritt. Beide Zweige sind als Kandidaten
geschlossen.

Die vorhandenen DTS-Runner sind an alte A/B/Gap-Grenzen und
kandidatenspezifische Sidecars gebunden. T1 allein liefert keine vollstaendige
S-Feldfortsetzung.

Klassifikation:

```text
SPECIALIZED_CLOSED_SURFACE_NOT_DIRECTLY_ADMISSIBLE
```

Eine spaetere Baselinezulassung duerfte ausschliesslich den eingefrorenen
Dreirollenkern unter einer neuen privaten S1-PZ-Bruecke ausfuehren. Keine
Gleichung, Rollenfolge oder Recoveryregel darf geaendert werden.

## L - Zustandsbehaftete Retentionsbaseline

`g2_d3_matched_retention_baseline.py` implementiert einen reinen
Einzustands-Retentionskern. Er akzeptiert jedoch ein G2-spezifisches
Fortsetzungsereignis, genau zwei identische Updates und liefert drei skalare
Checkpoints statt eines vollstaendigen F/T/I/C/R/U-Feldprofils.

Klassifikation:

```text
SPECIALIZED_CLOSED_SURFACE_NOT_DIRECTLY_ADMISSIBLE
```

Der Updatekern darf nicht still erweitert werden. Zuerst waere ein neuer
statischer Baselinevertrag erforderlich, der entscheidet, ob die unveraenderte
Einzustandsretention ueberhaupt ohne neue Funktionsannahme an die
S1-QA-Feldoberflaeche abbildbar ist.

## M - G2/D3-Rekonstruktionskontrolle

G2/D3 besitzt Schemata, Validatoren, Zweischrittkomposition,
Checkpointoperatoren und Comparatoren. Seine einzige ausgearbeitete endogene
Bildung wurde durch die Retentionsbaseline geschlossen; Free/Blocked wurde
durch Clamp und DTS/T1 reduziert.

Die vorhandenen Oberflaechen sind ereignis-, checkpoint- und
kandidatengebunden. Sie tragen keinen allgemeinen S1-PZ-Lebenszyklus.

Klassifikation:

```text
SPECIALIZED_CLOSED_SURFACE_NOT_DIRECTLY_ADMISSIBLE
```

G2/D3 darf spaeter nur als eingefrorene Rekonstruktionskontrolle auftreten.
Seine Rollen duerfen weder umbenannt noch als neuer Kandidatenzustand
uebernommen werden.

## Gesamtaudit

| Pflicht- oder Zusatzrolle | Vorhandener Kern | S1-QB-Status |
|---|---|---|
| aktueller Kontakt | ja, CarrierFrame | funktionaler Handoff fehlt |
| schneller H-Nachhall | ja, voller Feldkern | neue Huelle fehlt |
| mehrere feste Zeitskalen | nein | Kern fehlt |
| Fixed Adapter/Frozen/permanentes Gewicht | ja, B1 | neue Huelle fehlt |
| Integrator | ja, B2 | neue Huelle fehlt |
| Local Leaky | ja, B3 | neue Huelle fehlt |
| Linear/F3 Full/CONST-V | ja, B4-B6 | neue Huelle fehlt; Zusatzrollen |
| feste Verzoegerung | nur Probevergleich | Kern fehlt |
| statische Rekurrenz | nur privater Probehelfer | Kern fehlt |
| Replay | nein | Kern fehlt |
| Saettigung/Normalisierung | ja, W7-N-Skalarkerne | Feldhandoff ungeklaert |
| Capacity-Clamp | nur statische Abschlussregel | Lebenszykluskern fehlt |
| DTS-1/T1 | ja, geschlossen und spezialisiert | neue eingefrorene Baselinebruecke erforderlich |
| Retentionsbaseline | ja, G2-spezifisch | kein S1-QA-Feldhandoff |
| G2/D3-Kontrolle | ja, geschlossen und spezialisiert | keine direkte Zulassung |

Der Baselinebestand ist damit substanziell, aber nicht vollstaendig. S1-QA
darf noch nicht implementiert und kein Kandidat darf gegen eine absichtlich
unvollstaendige Gegenmenge bewertet werden.

## Gemeinsame Informationssperren

Jeder spaetere Baselineadapter muss folgende Grenze einhalten:

```text
gemeinsame Eingabe:
  vollstaendiges Feld
  Rezeptordistribution
  Schrittzeit
  Geometrieidentitaet

privater Kontext:
  Modellrolle
  vollstaendiger eigener Zustand
  eine eingefrorene Konfiguration

gesperrt:
  Kandidatenzustand und Kandidatenbilanz
  F/T/I/C/R/U-Armname
  A/B/C-Rollenbezeichnung
  erwartete Kontrastrichtung
  Checkpoint- und Ergebniswissen
  Zukunftszustand und Referenzvektor
  Retry-, Fit- oder Reparatursignal
```

Die Ausgabe muss ein vollstaendiges Feld, den vollstaendigen privaten
Folgezustand, endliche Diagnostik und einen kanonischen Eigendigest atomar
enthalten. Fehler duerfen keine Teilausgabe erzeugen.

Baselineadapter bleiben private Referenzinfrastruktur. Ihre Aufnahme in die
kuratierte aktive Feldkern-API ist nicht erforderlich und durch S1-QB nicht
freigegeben.

## Nichtduplizierungsregeln

- Frozen-E1, permanentes Gewicht und Fixed Adapter werden als eine statische
  Kopplungsklasse gefuehrt, solange keine getrennte Gegenprognose besteht.
- Mehrere einzeln passende Leaky-Arme sind keine Mehrzeitskalenbaseline.
- B4 ersetzt keine reine statische Rekurrenz.
- kapazitaetsbegrenztes F3 ersetzt keinen minimalen Capacity-Clamp.
- die G2-Retentionsbaseline ersetzt weder Replay noch allgemeinen
  Mehrzeitskalen-Nachhall.
- DTS-1/T1 und G2/D3 bleiben getrennte geschlossene Kontrollen und duerfen
  nicht als neuer Kandidat kombiniert werden.

## Fail-Closed-Bedingungen

Ein spaeterer Baselineanschluss wird gestoppt, wenn:

- ein Formadapter die Gleichung, Zustandsdimension oder Zeitinterpretation
  aendert;
- ein historischer Ergebnisvektor statt derselben neuen Geschichte verwendet
  wird;
- eine Baseline nur Readout, aber nicht das Geschichtspraefix erhaelt;
- privater Zustand zwischen Armen oder Refinements getragen wird;
- Arm-, Rollen-, Kandidaten- oder Ergebniswissen den Kern erreicht;
- ein skalischer Observeroutput ohne statischen Handoffvertrag zur
  Feldfortsetzung erklaert wird;
- eine fehlende Rolle durch eine fachlich andere vorhandene Baseline ersetzt
  wird;
- eine inkompatible Baseline aus dem Gesamtvergleich entfernt wird.

## Aussagegrenze

S1-QB ist ein Bestands- und Oberflaechenaudit. Es zeigt keine
Kandidatenfunktion und keine hypothetische MCM-Memory-Funktion. Es fuegt dem
primaeren MCM-Wahrnehmungsfeld keine Baseline und keinen Zustand hinzu.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QC - statischer Funktions-, Nichtduplizierungs- und
        Falsifikationsvertrag fuer das fehlende Pflichtbaselinepaket
```

S1-QC soll nur die kleinste fachlich eigenstaendige Menge fehlender
Baselinefunktionen binden. Fuer jede Rolle muessen Erklaerungsziel,
Abgrenzung zu vorhandenen Kernen, erforderlicher privater Zustand,
S1-PZ-Expositionspflicht, S1-QA-Ausgabe und Verwerfung feststehen. Noch keine
Gleichung, Parameter, Implementierung, Werte, Fixture, Runtimeaenderung,
Testausfuehrung oder Ergebnisentscheidung.
