# S1-TJ: Statischer Vertrag der modellneutralen Kandidaten-Beobachtungshuelle

## Status und Grenze

S1-TJ bindet ausschliesslich Rollen, Trennungen und Informationsgrenzen
einer spaeteren Kandidaten-Beobachtungshuelle. Die Huelle ist ein passives
Resultatbuendel und keine Kandidatenmechanik.

S1-TJ enthaelt:

- keinen Kandidaten und keine Ressourcenanatomie;
- keine Gleichung, Parameter, Werte oder Toleranzen;
- kein konkretes Serialisierungsschema und keine Digests;
- keine Implementierung, Tests oder Ausfuehrung;
- keine Funktions- oder Memory-Entscheidung.

## Grundform der Huelle

Eine spaetere Huelle muss atomar genau zwei logisch getrennte Ebenen tragen:

```text
CANDIDATE_FIELD_PROFILE
CANDIDATE_INTERNAL_EVIDENCE
```

Beide Ebenen muessen dieselbe Kandidaten-, Konfigurations-, Expositions-,
Frischzustands- und Ereigniskettenidentitaet referenzieren. Sie duerfen
weder ineinander eingebettet noch gegeneinander nachskaliert werden.

Das Feldprofil ist die einzige Kandidatenoberflaeche fuer den numerischen
Vergleich mit dem fixierten S1-TG-Atlas. Interne Belege bedienen nur die
harten S1-QA-Kandidatengates.

## H1 - Huellenidentitaet und Abschluss

Die Huelle muss spaeter mindestens binden:

- eigene Schema- und Vertragsidentitaet;
- eine vor Ausfuehrung registrierte, fachlich noch opake Kandidatenrolle;
- genau eine unveraenderte Konfigurationsidentitaet;
- Referenz auf die unveraenderte gemeinsame Exposition;
- Referenz auf den fixierten S1-TG-Baselineatlas;
- Quellen-, Geometrie-, Knotenordnungs- und Laufzeitprovenienz;
- einen atomaren Abschlussstatus und einen Eigendigest.

Eine Kandidatenrolle ist nur Orchestrierungs- und Provenienzmetadatum. Sie
darf dem Kandidatenkern waehrend eines Schritts nicht als Ergebnis-, Arm-
oder Zielinformation zufliessen.

## H2 - Gemeinsames Kandidatenfeldprofil

`CANDIDATE_FIELD_PROFILE` muss strukturell dieselbe oeffentliche Achse wie
jedes S1-TG-Baselineprofil tragen:

```text
17 geordnete F/T/I/C/R/U-Planrollen
40 geordnete Checkpoints
je Checkpoint Rezeptorkontakt, S und H an vier Knoten
320 signed S/H-Komponenten
vollstaendige Checkpoint- und Expositionsprovenienz
```

Zulaessig sind nur passive, nach einem abgeschlossenen Intervall oder einer
abgeschlossenen Probe aufgenommene Feldwerte. Die bestehende Knoten-, Plan-,
Checkpoint- und Komponentenordnung ist unveraenderlich.

Nicht in diese Ebene gehoeren:

- Ressourcenwerte oder kandidateninterne Zustandskoordinaten;
- Ablations- oder Nullpfadlabels;
- Comparatorstatus, Referenzresiduen oder Schwellen;
- ausgewaehlte Normen anstelle voller signed Vektoren;
- private Gleichungs-, Parameter- oder Diagnostikpayloads.

## H3 - Zustands- und Carryprovenienz

`CANDIDATE_INTERNAL_EVIDENCE` muss den vollstaendigen privaten
Kandidatenzustand an jedem registrierten Checkpoint kanonisch binden. Jeder
Zustandsbeleg muss eindeutig mit Feldcheckpoint, Carry, Konfiguration und
vorangegangener Ereigniskette verbunden sein.

Ein Zustandsdigest allein ist nur ein Vollstaendigkeits- und
Kontinuitaetsbeleg. Er darf keine Ressourcenbilanz, endogene Bildung,
Freigabe oder Wiederverwendung behaupten.

Jeder kandidatenfortschreibende Intervallschritt muss spaeter einen
passiven Uebergangsbeleg liefern, der Vorzustand, Nachzustand,
Ereignisquelle und Carrybezug verbindet. Observer oder Comparator duerfen
diesen Uebergang nicht selbst ausfuehren.

## H4 - Modellneutrale Bilanzbeobachtung

Die konkrete Kandidatenanatomie muss erst in einem spaeteren Vertrag ihre
lokalen Zustands- und Ressourcenrollen deklarieren. Die Huelle muss fuer
jede dann deklarierte Rolle ohne Sonderfall aufnehmen koennen:

- vollstaendige lokale Zustandskoordinaten je registriertem Ort;
- lokale Summe oder explizite lokale Dissipationsbuchung;
- globale Summe ueber die endliche Testgeometrie;
- alle Rollenwechsel und lokalen oder geometrischen Transfers;
- jeden zulaessigen Zu- oder Abfluss samt gleicher Kausalquelle;
- Vor- und Nachbilanz jedes relevanten Intervalls;
- Bilanzrest und vollstaendigen Zustandsbezug.

Die Huelle definiert weder Rollennamen noch Ressourcenzahl, Obergrenze oder
Erhaltungsgleichung. Sie verlangt nur, dass eine spaetere Kandidatendeklaration
vollstaendig und direkt beobachtbar abgebildet wird. Clipping,
Nachnormalisierung, stilles Nullsetzen und nicht beobachteter globaler
Speicher sind keine Bilanzbelege.

## H5 - Endogenitaets- und Kausalprovenienz

Jede spaeter beanspruchte Zustandsaenderung muss auf die geordnete normale
Feldgeschichte zurueckfuehrbar sein. Der zugehoerige Beleg muss unterscheiden:

- externe Rezeptor- und Feldfortsetzung;
- kandidateninternen Zustandsuebergang;
- passive Beobachtung;
- private Kontrollintervention fuer Ablation oder Vollpfaddeaktivierung.

Direktes Setzen einer Kandidatenressource, Recoverytoggle, Reset,
Ergebnislabel, Replay eines alten Sidecars oder Comparatorrueckkopplung sind
keine endogene Ursache und muessen fail-closed unzulaessig bleiben.

## H6 - Readoutablation

Fuer jeden spaeter als kandidatengetragen bewerteten Readout muss eine
passende `CANDIDATE_ABLATION_AT_READOUT`-Kontrolle vorliegen.

Die Huelle muss fuer Original und Ablation identisch binden:

- vollstaendiges Geschichtspraefix;
- Frischzustand und Konfiguration;
- aktuellen Rezeptorkontakt;
- angeglichenen S/H-Vorzustand;
- Geometrie, Zeitlage und Probe;
- Kandidatenzustand unmittelbar vor dem Readout.

Nur die kandidateninterne Rueckwirkung auf genau den betreffenden Readout
darf deaktiviert sein. Die Ablation darf keine vorausgehende Bildung,
Bilanz, Baseline oder Feldlage veraendern. Sie ist ein Kausalitaetsgate und
allein kein Funktionsbefund.

## H7 - Vollstaendiger Nullpfad

`CANDIDATE_DISABLED_FULL_PATH` beginnt aus dem gemeinsamen Frischzustand und
haelt den Kandidaten ueber die vollstaendige F/T/I/C/R/U-Exposition
deaktiviert.

Die Huelle muss diesen Pfad checkpointweise mit dem registrierten
Feldkern-Nullpfad verbinden. Rezeptor, S, H, Ticks, Geometrie, Ereignisse und
Feldfortsetzung muessen nach der spaeter vorregistrierten bitgenauen Regel
uebereinstimmen. Ein Kandidatenzustand darf im deaktivierten Pfad weder
verdeckt fortgeschrieben noch nachtraeglich entfernt werden.

Jede Nullpfadabweichung macht das Gesamtpaket technisch nicht berechenbar
und stoppt vor allen Funktionsgates.

## H8 - Freigabebeleg

Die R-Rollen muessen Feldprofil und interne Evidenz direkt verbinden:

- frueher und spaeter A-Readout unter angeglichener Feldlage;
- vollstaendige Kandidatenbilanz vor und nach jedem Gap;
- Funktionsverlust der frueheren A-Wirkung;
- direkt ausgewiesene erneut nutzbare lokale Kapazitaet;
- keine Freigabe durch Reset, Clipping, Neustart oder externen Schalter.

Ein sinkender Feldwert, verstrichene Zeit oder veraenderter Zustandsdigest
ist allein kein Freigabebeleg. Die konkrete Freigaberegel und ihre
Falsifikationsschwelle bleiben einem spaeteren Kandidatenvertrag vorbehalten.

## H9 - Wiederverwendungsbeleg

Die U-Rollen muessen auf einem gueltigen R-Freigabebeleg aufbauen. Die
Huelle muss gemeinsam tragen:

- direkte Bilanzlage unmittelbar vor der B-Geschichte;
- erneute lokale Beanspruchung waehrend derselben B-Geschichte;
- vollstaendigen B-Readout unter identischer B-Probe;
- zeitangepasste frische B-Kontrolle;
- fruehe, noch nicht freigegebene A-Kontrolle;
- lueckenlose Verbindung zwischen freigegebener und erneut beanspruchter
  lokaler Zustandsrolle.

Ohne gueltigen R-Beleg darf U weder als Wiederverwendung ausgewertet noch als
Teilstatus publiziert werden.

## Informationssperren

### Kandidatenproducer

Der Kandidatenproducer darf nur gemeinsame Exposition, aktuellen Feldzustand,
eigene registrierte Konfiguration und eigenen privaten Vorzustand erhalten.
Gesperrt sind Baselineprofile, Atlasdistanzen, Comparatorstatus, Armziele,
Ergebnislabels, Zukunftsereignisse und nachtraegliche Parameterwahl.

### Baselineproducer

Eine Baseline erhaelt nur dieselbe gemeinsame Exposition und ihren eigenen
privaten Zustand. Kandidatenbilanz, Ablationsrolle, Kandidatenzustand und
interne Kandidatenprovenienz bleiben unerreichbar.

### Passiver Observer

Der Observer darf abgeschlossene Feld-, Zustands-, Bilanz- und
Kontrollbelege aufnehmen und kanonisch binden. Er darf weder Modell noch
Feld fortschreiben, keine fehlende Beobachtung rekonstruieren und keine
Funktionsentscheidung treffen.

### Spaeterer Comparator

Der Comparator darf nur die vollstaendige unveraenderliche Huelle, den
fixierten S1-TG-Atlas und reine Vertrags-/Digesthelfer erhalten. Gesperrt
sind Kandidaten- und Baselinegleichungen, Runner, Orchestrator,
Fixturegeneratoren, private Zustandsparser, Parameterquellen, Retry,
Reparatur, Fit und Optimierung.

## Atomare Fail-Closed-Grenze

Die Huelle ist nur technisch vollstaendig, wenn gemeinsam vorliegen:

1. eindeutige Huellen-, Kandidaten-, Konfigurations- und Expositionsidentitaet;
2. vollstaendiges 40-Checkpoint-Feldprofil;
3. lueckenlose Zustands-, Carry- und Ereigniskettenprovenienz;
4. vollstaendige spaeter deklarierte Bilanzoberflaeche;
5. alle erforderlichen Readoutablationen;
6. vollstaendiger deaktivierter Nullpfad;
7. direkt verbundene R-Freigabebelege;
8. nur nach gueltigem R angebundene U-Wiederverwendungsbelege;
9. atomarer Abschluss ohne Teilresultat.

Fehlt ein Element, ist das gesamte Kandidatenpaket
`AUDIT_INVALID_NOT_COMPUTABLE`. Die Huelle selbst darf keinen positiven oder
negativen S1-PX-Funktionsstatus erzeugen.

## Aussagegrenze

S1-TJ definiert eine pruefbare technische Beobachtungsoberflaeche. Es gibt
weiterhin keinen Kandidaten, keine Gleichung und keinen Befund zu einer
hypothetischen MCM-Memory. Der S1-TG-Atlas, der primaere Feldkern und alle
geschlossenen Zweige bleiben unveraendert.

## Abschluss und naechster Schritt

```text
S1_TJ_MODEL_NEUTRAL_CANDIDATE_OBSERVATION_ENVELOPE_BOUND
FIELD_PROFILE_INTERNAL_EVIDENCE_AND_INFORMATION_BARRIERS_SEPARATED
ATOMIC_COMPLETENESS_REQUIRED_BEFORE_ANY_CANDIDATE_COMPARISON
NO_ANATOMY_NO_VALUES_NO_IMPLEMENTATION_NO_RUN
```

Der einzige naechste Schritt ist S1-TK als statischer Schema-,
Kardinalitaets- und Fail-Closed-Validierungsvertrag fuer diese Huelle.
S1-TK darf nur die exakten unveraenderlichen Recordfamilien, Referenzen,
Ordnungen und Fehlerklassen binden. Kandidatenanatomie, Gleichung,
Parameterwerte, Implementierung, Tests, Ausfuehrung und Ergebnisentscheidung
bleiben gesperrt.
