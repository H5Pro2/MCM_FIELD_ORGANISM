# S1-QZ: Statischer gemeinsamer Baselinearm-, Carry- und S1-PZ-Lebenszyklus-Huellenvertrag

## Status und Umfang

S1-QZ bindet die gemeinsame aeussere Vertragsform, unter der die in S1-QY
klassifizierten Pflichtbaselinekerne spaeter dieselben modellneutralen
S1-PZ-Geschichten tragen koennen.

Der Vertrag bindet ausschliesslich:

- technische Baseline-Modellidentitaeten;
- getrennte Expositionsreplik- und Orchestrierungsidentitaeten;
- Frischstart-, Feld- und Privatcarryrollen;
- eine gemeinsame technische Intervalluebergabe;
- atomare Erfolgs- und Fehlerausgaben;
- die rein aeussere Abbildung der S1-PZ-Ereignisrollen;
- die Brueckengrenzen fuer A2/B1-B6 und M4.

S1-QZ bindet keine Geometrie, Dauer, Zahl, Konfiguration, Toleranz, Fixture,
Matrixzelle oder Comparatorentscheidung. Es implementiert und testet nichts
und fuehrt keinen Feldlauf aus.

Verbindliche Entscheidung:

```text
COMMON_BASELINE_MODEL_ROLE_AND_REPLICA_IDENTITY_SEPARATED
FRESH_FIELD_PRIVATE_CARRY_AND_ATOMIC_INTERVAL_RESULT_BOUND
S1PZ_EVENTS_MAPPED_ONLY_BY_OUTER_LIFECYCLE_ENVELOPE
A2_AND_M4_REUSE_ALLOWED_ONLY_AS_EXACT_NEUTRAL_BRIDGES
MATRIX_COMPARATOR_IMPLEMENTATION_AND_EXECUTION_REMAIN_BLOCKED
```

## Zwei getrennte Identitaetsebenen

### Baseline-Modellrolle

Die Modellrolle bezeichnet genau eine technische Gegenbaseline und bleibt
ueber alle F/T/I/C/R/U-Geschichten unveraendert. S1-QZ bindet folgende
zulaessige Rollenidentitaeten:

```text
A0_CURRENT_CONTACT
A1_FAST_SH
A2_B1_FIXED_ADAPTER
A2_B2_INTEGRATOR
A2_B3_LOCAL_LEAKY
A2_B4_LINEAR_COUPLED
A2_B5_F3_FULL
A2_B6_CONST_V
A3_NORM
M1_PARALLEL_LEAK
M2_DELAY
M2_REPLAY
M4_DTS1_T1
M5_DIRECT
```

Die Liste ist eine Rollenregistrierung, keine Ausfuehrungsmatrix. A3-SAT,
M3, G2/D3, Frozen-E1 und statische Rekurrenz sind keine zusaetzlichen
Feldarmrollen.

### Expositionsreplik

Die Replikidentitaet gehoert ausschliesslich zur Orchestrierung. Sie bindet
spaeter Familie, Expositionsarm, Frischreplik und Ereignisposition. Eine
Modellrolle darf diese Identitaet weder als Eingabe erhalten noch aus einem
Konfigurationsfeld oder Privatstatus rekonstruieren.

Damit gilt:

```text
MODEL_ROLE bestimmt den privaten technischen Kern.
REPLICA_ROLE bestimmt nur die aeussere kausale Ereignisfolge.
```

Eine Baseline sieht die realen technischen Inputs der Geschichte, aber nicht
deren Bezeichnungen `F_A`, `I_LOCAL`, `R_LATE` oder vergleichbare
Forschungsrollen.

## Gemeinsamer Registrierungsbeleg pro Modellrolle

Vor jeder spaeteren Matrix muss jede Modellrolle genau einen unveraenderlichen
Registrierungsbeleg besitzen. Dieser belegt mindestens:

- Modellrollen- und Adaptervertragsidentitaet;
- private Zustands- oder Zustandslosklasse;
- Konfigurationsidentitaet und Konfigurationsdigest;
- Frischzustandsfabrik;
- zulaessige synchrone und/oder transiente Intervallform;
- vollstaendigen Feldoutput;
- atomaren Fehlerstatus;
- die erlaubte technische Diagnostikoberflaeche.

Der Beleg darf keine Familie, Expositionsreplik, erwartete Richtung,
Checkpointrolle oder Ergebnisreferenz enthalten. Kann eine Modellrolle nicht
mit genau einem Beleg alle spaeteren Geschichten tragen, ist sie
`NOT_CONNECTABLE` und das gesamte Paket bleibt gesperrt.

## Frischprojektion und Modellprivatheit

Jede Expositionsreplik jeder Modellrolle startet unabhaengig. Der Frischstart
besteht aus:

1. derselben registrierten oeffentlichen Feldprojektion;
2. dem privaten Frischzustand genau dieser Modellrolle oder einer kanonischen
   Zustandslosmarkierung;
3. einer neuen leeren Provenienzkette;
4. derselben Konfigurationsidentitaet wie alle anderen Repliken dieser
   Modellrolle.

Die oeffentliche Frischprojektion umfasst die vergleichbaren Feldrollen,
insbesondere Geometrie, Knotenordnung, Rezeptorlage, S, H und Feldzeit. Ein
modelleigenes eingebettetes Ledger oder ein privater Substratzustand ist kein
oeffentlicher Feldunterschied, muss aber getrennt und vollstaendig belegt
werden.

Digestgleichheit gilt:

- fuer die oeffentliche Frischprojektion ueber alle Modellrollen;
- fuer den vollstaendigen Frischzustand zwischen Repliken derselben
  Modellrolle;
- nicht fuer unterschiedliche private Modellklassen untereinander.

Ein B1-Frischzustand muss daher nicht denselben Privatdigest wie M2 oder M4
besitzen. Eine Replik darf aber niemals aus dem Endzustand einer anderen
Replik aufgebaut oder durch Nullsetzen eines gebrauchten Zustands erzeugt
werden.

## Gemeinsame Carryklassen

Jede erfolgreiche Intervallausgabe traegt immer das vollstaendige Folgefeld.
Zusaetzlich gilt genau eine der folgenden Privatcarryklassen:

| Carryklasse | Modellrollen | Gebundene Bedeutung |
|---|---|---|
| `STATELESS_MARKER` | A0 | kein privater Zustand und kein Verlauf |
| `FIELD_ONLY` | A1 | S/H liegen ausschliesslich im vollstaendigen Feld |
| `OPAQUE_PRIVATE_STATE` | A2/B1-B6, A3-NORM, M1, M2, M5 | vollstaendiger rollenprivater Zustand, fuer die Huelle inhaltlich undurchsichtig |
| `OPAQUE_THREE_ROLE_LEDGER` | M4 | vollstaendiges eingefrorenes Dreirollenledger samt Validierungsbeleg |

`OPAQUE` bedeutet, dass die gemeinsame Huelle den Zustand nur nach Typrolle,
Identitaet und Digest prueft und weiterreicht. Sie darf keine lokalen Werte,
Pufferpositionen, Spuren oder Ressourcenrollen auslegen.

Feld und Privatcarry bilden einen unteilbaren Replikzustand. Nach einem
Fehler darf keiner von beiden als neuer Vorzustand verwendet werden.

## Gemeinsame technische Intervalluebergabe

Ein normaler Modellaufruf erhaelt genau eine unveraenderliche technische
Intervalluebergabe mit:

- Modellrollen- und Adaptervertragsidentitaet;
- Konfigurationsidentitaet;
- vollstaendigem Feldvorzustand;
- privatem Vorzustand oder Zustandslosmarkierung;
- kanonischer Geometrie- und Knotenidentitaet;
- aktuellem Rezeptorinput oder einer transienten Rezeptorfolge;
- abgeschlossenem technischen Zeitintervall;
- getrennten Eingabe-, Feld-, Privatstatus- und Intervalldigests.

Nicht uebergeben werden:

- S1-PZ-Familie oder Ereignisrollenname;
- Expositionsreplik, Ordinal oder Checkpointbezeichnung;
- `HISTORY`, `GAP`, `PROBE`, `ALIGN` oder `OBSERVE` als Modelllabel;
- Kandidatenzustand, Bilanz, Kapazitaet oder Ablationsrolle;
- Zielrichtung, Referenzprofil, Comparatorstatus oder Zukunftsdaten;
- Retry-, Fit-, Reparatur- oder Optimierungsanweisungen.

Ein Gap erscheint am Modellaufruf nur als normaler registrierter
Nullkontaktinput. Eine A-, B- oder C-Geschichte unterscheidet sich nur durch
ihren realen Rezeptor- und Geometrieinput, nicht durch ein Rollenflag.

## Atomare gemeinsame Intervallausgabe

Jeder private Adapter muss nach genau einem Intervall ein gemeinsames
Ergebnis liefern, das mindestens belegt:

- Modellrollen-, Vertrags- und Konfigurationsidentitaet;
- Eingabe-, Feldvorzustands-, Privatvorzustands- und Geometriedigest;
- vollstaendiges Folgefeld;
- vollstaendigen Privatfolgezustand oder die richtige Leermarkierung;
- Digest des Folgefeldes und des Privatfolgezustands;
- getrennten technischen Diagnostikdigest;
- korrekte Feldzeitfortschreibung;
- einen kanonischen Abschlussstatus und Eigendigest.

Erlaubte Abschlussklassen sind nur:

```text
COMPLETED
NOT_COMPUTABLE
```

Bei `NOT_COMPUTABLE` werden weder Folgefeld noch Privatfolgezustand
veroeffentlicht. Ein Exceptionpfad, der einen Teilzustand nach aussen gibt,
ist nicht anschliessbar. Die gemeinsame Huelle darf einen privaten Fehlercode
in kanonische Provenienz aufnehmen, ihn aber nicht reparieren oder als
fachliches Ergebnis interpretieren.

## Aeussere Abbildung der S1-PZ-Ereignisse

Nur die Lebenszyklushuelle kennt die Ereignisrollen. Sie bildet sie wie folgt
auf technische Operationen ab:

| S1-PZ-Rolle | Aeussere Operation | Modellaufruf |
|---|---|---|
| `HISTORY_A` | geordnete normale Kontaktintervalle an A | einmal pro registriertem Intervall |
| `HISTORY_B_LOCAL` | geordnete normale Kontaktintervalle an B | einmal pro registriertem Intervall |
| `HISTORY_C_REMOTE` | geordnete normale Kontaktintervalle an C | einmal pro registriertem Intervall |
| `GAP_ZERO_CONTACT` | geordnete normale Nullkontaktintervalle | einmal pro registriertem Intervall |
| `PROBE_A` | wertidentisches normales A-Probeintervall | genau der registrierte Probeaufruf |
| `PROBE_B` | wertidentisches normales B-Probeintervall | genau der registrierte Probeaufruf |
| `ALIGN_READOUT_SH` | zeitlose aeussere Feldangleichung | keiner |
| `OBSERVE` und benannte C-Checkpoints | passiver Snapshot | keiner |

Die Huelle darf keine Ereignisse zusammenfassen, aufteilen, wiederholen oder
ueberspringen. Ob ein technisches Intervall synchron oder transient ist,
folgt ausschliesslich aus der registrierten Eingabeform.

## Zeitloses ALIGN_READOUT_SH

Die Angleichung ist kein Baselineadapter und kein Feldschritt. Sie darf nur:

- aktuellen Rezeptorkontakt, oeffentliches S und oeffentliches H auf die
  registrierte gemeinsame Vergleichslage setzen;
- die oeffentliche Angleichungsprovenienz dokumentieren;
- das vollstaendige Feld ohne Zeitfortschreibung ausgeben.

Sie muss bitgenau erhalten:

- privaten Zustand oder Ledger;
- Konfigurations- und Modellrollenidentitaet;
- Geometrie und Knotenordnung;
- Feldzeit;
- alle nicht angeglichenen modelleigenen Payloads.

Die Huelle darf privaten Zustand weder lesen noch serialisiert neu aufbauen.
Eine Modellrolle, deren private Identitaet durch die reine S/H-Angleichung
nicht erhalten werden kann, ist `NOT_CONNECTABLE`.

## Passive OBSERVE-Operation

`OBSERVE` ruft keinen Adapter auf und veraendert weder Feld noch Privatcarry.
Ein Beobachtungsrecord darf nur enthalten:

- Modellrolle und aeussere Replik-/Checkpointprovenienz;
- oeffentliche Feldprojektion mit vollstaendigem signed S und H;
- Feld-, Geometrie-, Zeit-, Konfigurations- und Privatstatusdigest;
- technischen Gueltigkeitsstatus und Eigendigest.

Private Rohzustaende, Armziele und erwartete Kontraste werden nicht in einen
allgemeinen Beobachtungsrecord kopiert. Kandidatenbilanz und M3 bleiben
getrennte spaetere Vertragsoberflaechen.

## Lebenszykluszustand und Abbruchregel

Die aeussere Huelle traegt pro Modellrolle und Expositionsreplik genau:

- den aktuellen unteilbaren Replikzustand aus Feld und Privatcarry;
- den unveraenderten Modellregistrierungsbeleg;
- die aktuelle Position im vorregistrierten Ereignisplan;
- eine geordnete Kette erfolgreicher Intervall-, Align- und
  Beobachtungsreceipts;
- einen atomaren Replikstatus.

Nur die Huelle kennt die Planposition. Ein Fehler stoppt die betreffende
Replik sofort als `NOT_COMPUTABLE`. Es gibt keinen Retry, Ersatzarm,
Ruecksprung, Reset oder Weiterlauf mit dem letzten gueltigen Teilzustand. Ein
spaeteres Gesamtbuendel muss schon bei einer fehlenden Pflichtreplik
fail-closed bleiben.

## A0- und A1-Anschlussgrenze

A0 darf den vorhandenen feldnativen aktuellen Kontaktpfad verwenden. Sein
Output darf nur vom aktuellen technischen Input abhaengen; der uebergebene
Feldvorzustand dient ausschliesslich der Feld-, Geometrie- und
Zeitfortschreibung. Jede private Verlaufsbildung sperrt A0.

A1 darf ausschliesslich die vorhandenen schnellen synchronen oder
transienten S/H-Feldkerne verwenden. Es besitzt keinen zusaetzlichen
Privatcarry. Eine zweite H-Kopie, armweise H-Konfiguration oder
kandidatenbezogener Zustand sperrt A1.

## A2/B1-B6-Brueckengrenze

Die bestehenden privaten B1-B6-Intervallkerne duerfen nur hinter je einem
reinen rollenfesten Adapter angeschlossen werden. Eine Bruecke ist nur rein,
wenn sie:

- die gemeinsame technische Intervalluebergabe typ- und formgleich in den
  bereits akzeptierten Kernaufruf ueberfuehrt;
- dieselbe unveraenderte B-Rollenkonfiguration und Privatstatusanatomie
  erhaelt;
- das vorhandene vollstaendige Feld, den Privatfolgezustand und die
  Diagnostik ohne Nachberechnung uebernimmt;
- weder Profilnamen noch alte Fall-, Arm- oder Ergebnisrollen weitergibt.

Historische Geometrie-, Refinement- oder Konfigurationsregistrierungen
duerfen nur verwendet werden, wenn die spaetere gemeinsame Registrierung
formal exakt kompatibel ist. Eine Bruecke darf keine neue Geometriemappingzeile
erfinden, keinen Refinementwert ersetzen und keine Gleichung verallgemeinern.

Ist mindestens eine B1-B6-Rolle nicht exakt anschliessbar, lautet ihr Status
`NOT_CONNECTABLE`; sie darf weder entfallen noch durch eine andere A2-Rolle
ersetzt werden.

## A3-, M1-, M2- und M5-Anschlussgrenze

Die vorhandenen atomaren privaten Kompositoren duerfen nur durch
Formadapter vereinheitlicht werden:

- `A3_NORM` uebernimmt Feld und vollstaendigen NORM-Folgezustand;
- `M1_PARALLEL_LEAK` uebernimmt Feld und vollstaendigen Zweispurfolgezustand;
- `M2_DELAY` und `M2_REPLAY` uebernehmen je getrennt Feld und vollstaendigen
  Pufferfolgezustand;
- `M5_DIRECT` uebernimmt Feld und vollstaendigen Einzustandsfolgezustand.

Die Huelle darf ihre privaten Receipts validieren und digestsicher kapseln,
aber keine Outputrolle, Quellposition, Spur, Skalierungsgrundlage oder
Retentionskoordinate umdeuten. M2-Modi teilen weder Puffer noch Replikcarry.

## M4-Brueckengrenze

M4 darf nur den geschlossenen DTS-1-Feldschritt und die T1-Validierung der
unveraenderten `free/bound/blocked`-Anatomie verwenden. Eine neutrale Bruecke
darf:

- normale gemeinsame Kontakt- und Nullkontaktintervalle uebergeben;
- Feld und vollstaendiges Dreirollenledger gemeinsam tragen;
- vorhandene lokale Erhaltungsvalidierung und Diagnostik kapseln.

Sie darf nicht:

- Recovery-on/off-, Profil-, Kandidaten- oder G2/D3-Sidecars aufrufen;
- eine neue Ressourcenrolle, Freigaberegel oder Feldrueckwirkung einfuehren;
- T1 als zweiten dynamischen Zustand ausfuehren;
- Ereignisrollen in private Ledgeroperationen uebersetzen.

Kann der unveraenderte M4-Kern einen normalen S1-PZ-Nullkontaktverlauf nicht
ohne Sidecar tragen, bleibt M4 `NOT_CONNECTABLE` und der Gesamtvergleich
gesperrt.

## Paketweite Fail-Closed-Regeln

S1-QZ wird verletzt, wenn spaeter:

- Modellrolle und Expositionsreplik vermischt werden;
- eine Baseline Familie, Ereignisname, Ziel oder Ergebniswissen erhaelt;
- oeffentliche Frischprojektionen nicht identisch registriert sind;
- private Frischzustaende, Felder oder Carries zwischen Repliken geteilt
  werden;
- eine Huelle private Zustandswerte interpretiert oder repariert;
- `ALIGN_READOUT_SH` Zeit oder Privatstatus veraendert;
- `OBSERVE` einen Modellkern aufruft;
- Intervallfehler einen Teiloutput freigeben;
- A2 eine alte Profilhuelle oder neue Kernregel uebernimmt;
- M4 einen Recovery-Sidecar oder eine neue Ressourcenfunktion verwendet;
- eine inkompatible Pflichtrolle still entfaellt;
- Matrix oder Comparator vor Abschluss der Anschlusspruefung ausgefuehrt
  werden.

## Aussagegrenze

S1-QZ bindet nur die gemeinsame technische Transport- und
Lebenszyklusoberflaeche. Es existiert noch keine implementierte Huelle, keine
Matrix, kein Comparator, kein Feldlauf und kein Funktionsbefund. Eine
hypothetische MCM-Memory bleibt eine offene Entwicklungsrichtung. Der
primaere MCM-Wahrnehmungsfeldkern und alle geschlossenen Zweige bleiben
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RA - statischer Pflichtbaselinepaket-Arm-, Familien- und
        Checkpointmatrix- sowie atomarer Gesamtresultatbuendelvertrag
```

S1-RA soll ausschliesslich die vollstaendige Kreuzung der in S1-QZ
registrierten Modellrollen mit den S1-PZ-Expositionsrepliken und
Beobachtungspunkten binden. Es muss Vollstaendigkeit, getrennte Frischstarts,
Carryketten, gemeinsame Provenienz und atomaren Paketabbruch festlegen. Noch
keine konkreten Inputs, Zeiten, Parameter, Toleranzen, Comparatorlogik,
Implementierung, Fixture, Testausfuehrung oder Feldlauf.
