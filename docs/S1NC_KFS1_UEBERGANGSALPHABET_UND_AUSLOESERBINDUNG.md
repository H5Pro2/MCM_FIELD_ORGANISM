# S1-NC KFS-1 Uebergangsalphabet und Ausloeserbindung

## Status

S1-NC bindet ausschliesslich, welche lokalen Ressourcenwechsel fuer `KFS-1`
strukturell zulaessig waeren und welche lokale Beobachtung einem solchen
Wechsel vorausgehen muesste. Der Schritt enthaelt keine Kandidatengleichung,
keine Rate, keine Parameter, keine Runtimeintegration und keinen Feldlauf.

Das Uebergangsalphabet beweist keine Wirkung. Es verhindert nur, dass eine
spaetere Dynamik beliebige oder nachtraeglich passend gemachte
Ressourcenwechsel verwenden kann.

## Lokale Grundregel

Jeder tatsaechliche Ressourcenwechsel gehoert genau einer registrierten
`edge_id`. Quelle und Ziel liegen im selben lokalen Ressourcenkonto. Die
Kapazitaet der Kante bleibt unveraendert, und die Verringerung der Quellrolle
muss exakt der Erhoehung der Zielrolle entsprechen.

Ressource darf weder erzeugt noch geloescht, zwischen Kanten verschoben oder
aus einem globalen Ausgleichstopf bezogen werden. Diese Aussage ist eine
Erhaltungsbedingung und noch keine Dynamikgleichung.

## Zulaessige Ressourcenwechsel

S1-NC erlaubt genau vier tatsaechliche Wechsel:

| Uebergangs-ID | Quelle | Ziel | Erforderliche lokale Ausloeserklasse |
|---|---|---|---|
| `LOCAL_CONTACT_BIND` | `free` | `bound` | registrierte lokale Kontaktbeobachtung am read-only S/H-Feldbezug derselben Kante |
| `LOCAL_BOUND_RELEASE` | `bound` | `free` | registrierte lokale Loesungsbeobachtung nach gebundener Vorgeschichte |
| `LOCAL_REFRACTORY_ENTRY` | `bound` | `blocked` | registrierte lokale Abschlussbeobachtung einer zuvor gebundenen Beanspruchung |
| `LOCAL_REFRACTORY_RELEASE` | `blocked` | `free` | registrierte lokale Loesungsbeobachtung nach refraktaerer Vorgeschichte |

Die Ausloeserklassen benennen nur die spaeter erforderliche kausale Rolle.
Sie legen weder Schwellenwert noch Staerke, Rate, Dauer oder
Uebergangswahrscheinlichkeit fest.

`LOCAL_CONTACT_BIND` gilt auch fuer eine spaetere Wiederbindung. Eine
Wiederbindung ist nur zulaessig, wenn die betreffende Ressource zuvor wieder
als `free` bilanziert wurde. Es gibt keinen direkten Sonderweg in `bound`.

## Zulaessiger Stillstand

Eine Ressourcenrolle darf innerhalb einer Beobachtungsgrenze unveraendert
bleiben:

| Stillstands-ID | Rolle |
|---|---|
| `HOLD_FREE` | `free` bleibt `free` |
| `HOLD_BOUND` | `bound` bleibt `bound` |
| `HOLD_BLOCKED` | `blocked` bleibt `blocked` |

Stillstand ist kein Ressourcenwechsel und kein positiver Kandidatenbefund.
Er benoetigt keinen erfundenen Ausloeser. Ein spaeterer Record muss Stillstand
und tatsaechliche Verschiebung eindeutig unterscheiden.

## Verbotene Wechsel

Folgende Strukturen sind fail-closed gesperrt:

- `free -> blocked`, weil eine registrierte Bindung uebersprungen wuerde;
- `blocked -> bound`, weil Freigabe und erneute Beanspruchung verschmolzen
  wuerden;
- jeder Wechsel zwischen verschiedenen `edge_id`-Konten;
- jeder Wechsel aus oder in eine nicht registrierte vierte Ressourcenrolle;
- gleichzeitige Zuordnung derselben Ressourcenmenge zu mehreren Zielrollen;
- negative, nicht endliche oder die Quellrolle uebersteigende Verschiebung;
- Aenderung der registrierten Kantenkapazitaet;
- Nettoverrechnung mehrerer gegenlaeufiger Wechsel ohne einzelne
  Uebergangsrecords;
- Wechsel, die erst durch Readout, Klassifikator, Label, Reward, Zielwert oder
  Ergebnisgrenze festgelegt werden;
- Wechsel ohne vorangehenden gueltigen KFS-1-Anatomie- und
  Expositionsbeleg.

## Kausale Ausloeserbindung

Ein tatsaechlicher Wechsel darf spaeter nur akzeptiert werden, wenn ein
unveraenderlicher lokaler Ereignisbeleg mindestens folgende Identitaeten
bindet:

- `event_id` und `transition_id`;
- dieselbe `edge_id` fuer Vorzustand, Beobachtung und Nachzustand;
- `field_interval_id` und einen streng geordneten `event_ordinal` innerhalb
  der technischen Feldfolge;
- `source_role` und `target_role`;
- Vor- und Nachzustandsdigest des vollstaendigen lokalen Ledgers;
- `field_reference_digest` der read-only Ausloeserbeobachtung;
- `exposure_history_digest` der relevanten Vorgeschichte;
- `trigger_observation_digest` ohne Rohdaten oder semantische Labels;
- einen eigenen `event_digest`.

`field_interval_id` und `event_ordinal` ordnen die technische Feldfolge. Eine
externe Rechner- oder Systemuhr ist keine kausale Quelle.

## Atomare Zuordnung

Ein Uebergangsrecord besitzt genau eine Quellrolle und genau eine Zielrolle.
Wenn innerhalb derselben Feldgrenze mehrere Ressourcenanteile unterschiedliche
Ziele erhalten sollen, muessen sie als getrennte, streng geordnete Ereignisse
erscheinen. Ihre Vor- und Nachzustandsdigests muessen lueckenlos verkettet
sein.

Ein spaeterer Validator darf gegenlaeufige Ereignisse nicht zu einem
scheinbaren Nullwechsel zusammenziehen. Bruttoereignisse bleiben sichtbar,
damit Abschwaechung, Freigabe und Wiederbindung getrennt pruefbar bleiben.

## Abgrenzung der Ausloeserrolle

Die lokale Feldbeobachtung darf einen Wechsel spaeter nur kausal begrenzen;
sie schreibt das Ledger nicht selbst. Der lokale Zustandswechsel muss ein
interner KFS-1-Zustandsvorgang bleiben. Passive Messrollen beobachten
Vorzustand, Ereignis und Nachzustand, erzeugen aber keinen davon.

Damit bleiben insbesondere gesperrt:

- ein Fixed Adapter, der den Wechsel bereits vor der Probe festlegt;
- ein Integrator, dessen Akkumulation nur in Ressourcenrollen umbenannt wird;
- Leaky-Nachhall als scheinbare Freigabe ohne lokales Ledger;
- Replay oder Sequenzpuffer als Ausloeser;
- globale Normalisierung als Ersatz fuer eine lokale Ursache;
- ein Readout, das den Ereignistyp erst nach dem Ergebnis bestimmt.

## Faire Baselinehistorie

Kandidat und zustandsbehaftete Baselines muessen dieselbe relevante geordnete
Kontakt-, Gap- und Folgegeschichte erhalten. Eine Baseline ohne
Ressourcenledger erhaelt den expliziten Status `transition_not_applicable`.
Fuer sie werden keine kuenstlichen Null-Ledger oder KFS-1-Ereignisse erzeugt.

## Statische Falsifikationsgrenze

Der Uebergangspfad wird vor jeder Gleichung gestoppt, wenn:

- ein benoetigter Funktionsfall einen verbotenen Wechsel voraussetzt;
- lokale Ursache und lokaler Ledgerwechsel nicht derselben Kante zugeordnet
  werden koennen;
- Erhaltung nur durch globale Korrektur herstellbar ist;
- Ereignisreihenfolge oder Vorgeschichte nicht reproduzierbar bindbar ist;
- Readout oder Ergebniswissen fuer die Wahl des Uebergangs erforderlich ist;
- Fixed Adapter, Leaky-Nachhall, Integrator oder Replay dieselbe Struktur ohne
  das lokale KFS-1-Ledger vollstaendig erklaert.

## Erlaubte Vertragstests

S1-NC erlaubt spaeter ausschliesslich statische Tests auf:

- Vollstaendigkeit der vier Wechsel und drei Stillstandsrollen;
- Sperre aller nicht registrierten Rollenpaare;
- gleiche lokale Kantenidentitaet in Vorzustand, Ausloeser und Nachzustand;
- unveraenderte Kapazitaet und exakte lokale Verschiebungsbilanz;
- eindeutige Ereignisordnung und lueckenlose Digestverkettung;
- Trennung von Ereignis, passiver Messung und Baseline;
- deterministische Fail-Closed-Ablehnung verbotener Wechsel.

Nicht erlaubt sind Tests auf Uebergangswirkung, Rate, Abschwaechungsstaerke,
Interferenzstaerke, spaetere Feldaufnahme oder hypothetische MCM-Memory.

## Ergebnis von S1-NC

S1-NC reduziert den moeglichen KFS-1-Mechanismus auf vier lokale,
ressourcenerhaltende Wechsel und drei klar getrennte Stillstandsrollen. Damit
ist die Ueberlegung weiter technisch konsistent, aber noch nicht dynamisch
definiert oder funktional bestaetigt.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-ND, ausschliesslich als statischer Schema- und
Digestvertrag fuer KFS-1-Uebergangsrecords. Er darf Pflichtfelder,
Vor-/Nachzustandsverkettung, Ausloeserreferenzen, Fehlercodes und
Fail-Closed-Pruefungen binden. Gleichung, Rate, Parameter,
Runtimeintegration, Feldlauf und Funktionsentscheidung bleiben gesperrt.
