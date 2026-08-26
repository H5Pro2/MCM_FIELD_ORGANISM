# S1-EB18: Fachliche Freigabepruefung

## Entscheidung

```text
KORREKTUR
```

Der S1-EB-Korridor ist fachlich sinnvoll und technisch vollstaendig
vorbereitet. Eine unmittelbare Ausfuehrungsfreigabe ist dennoch noch nicht
begruendet, weil zwei vor dem Einmallauf notwendige Festlegungen fehlen:

1. eine statische Vertragspruefung;
2. ein festes Ressourcen- und Laufzeitfenster fuer genau diesen Lauf.

Das ist kein wissenschaftlicher `STOPP` und keine Sackgasse. Die Korrektur
betrifft nur die Freigabedisziplin vor dem einmaligen Lauf.

## Gepruefte Forschungsfrage

```text
Trennt r8 beide feinen Probensignale vom vorregistrierten numerischen Rest?
```

Die Frage ist eng und falsifizierbar. Sie prueft nicht, ob E1 Memory,
Semantik oder KI ist. Sie prueft nur, ob die bereits beobachtete
reihenfolgeabhaengige Zustandsbildung und spaetere Feldantwort unter der
feineren `r2/r4/r8`-Diskretisierung robust vom eigenen numerischen Rest
getrennt werden kann.

## Bewertung der Kontrollen

Fuer diese enge technische Frage sind die gebundenen Kontrollen geeignet:

- AB und BA besitzen dieselben Supports, Abschlusszeiten und
  Kontaktintegrale; nur die Reihenfolge unterscheidet sich.
- `r2/r4/r8` veraendert nur die Unterteilung kontaktfreier Intervalle.
- P0 trennt den neutralen Feldpfad.
- Bildungsablation prueft, ob der E1-Zustand fuer die spaetere Wirkung
  erforderlich ist.
- Probeablation prueft die kausale Rueckwirkung des eingefrorenen Zustands.
- Fixed Adapter prueft, ob die Probeausgabe durch den konkret angewandten
  Adapter erklaert wird.
- AB-Identitaetswiederholung, lokale Ressourcenbilanz und Exactly-once-
  Supportzuordnung kontrollieren Determinismus und technische Konsistenz.
- `r2/r4` und `r4/r8` liefern zwei getrennte numerische Reststufen.

Diese Kontrollen reichen fuer die vorregistrierte technische Entscheidung.
Sie reichen ausdruecklich nicht fuer einen allgemeinen Memory- oder
Neuheitsnachweis gegen alle denkbaren Substratbaselines.

## Bewertung der Entscheidungsregel

Die vier Ergebnisse sind vorab eindeutig gebunden:

```text
TECHNICALLY_INVALID
NO_CONFIRMED_REFINED_EFFECT
CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT
NUMERICALLY_UNDECIDABLE
```

Die strikte Achtfachgrenze bleibt unveraendert. Gleichheit mit dem Boden ist
kein Bestehen. Nachtraegliche Schwellenanpassung, Parametrierung oder
Umdeutung von S1-EA6 bleibt verboten. Damit ist die Auswertung gegen den
knappen S1-EA6-Ausgang ausreichend geschuetzt.

## Bewertung der Aussagegrenze

Die Aussagegrenze ist fachlich korrekt:

- Ein positives Ergebnis wuerde nur einen verfeinert bestaetigten
  technischen Weltbildungs- und Transfer-Effekt belegen.
- `NUMERICALLY_UNDECIDABLE` bleibt ein gueltiges Ergebnis und kein Fehler.
- Ein negatives Ergebnis widerlegt nicht das gesamte MCM-Projekt.
- Kein Ausgang erlaubt unmittelbar Claims zu Memory, Semantik,
  Organisation, Topologie, Selbstregulation, Erleben oder KI.
- S1-EA6 bleibt terminal und wird weder wiederholt noch ueberschrieben.

## Ressourcen- und Fehlergrenze

Das statisch bekannte Schrittinventar betraegt:

```text
Bildung: 5 Arme * (400 + 800 + 1600) = 14000 Feldschritte
Probe:    7 Arme * (200 + 400 + 800)  =  9800 Feldschritte
Gesamt:                                  23800 Feldschritte
```

Vor der Freigabe fehlen weiterhin ein fester maximaler Zeitrahmen und eine
feste Speichergrenze fuer diesen kanonischen Lauf. Beide Grenzen muessen vor
Ausfuehrungsbeginn festgelegt werden und duerfen nicht anhand eines
Teilergebnisses erweitert werden.

Die Fehlerpolitik ist dagegen bereits geeignet:

- Ein gestarteter Fehler behaelt den Attemptmarker.
- Es erfolgt kein automatischer Retry.
- Der belegte Pfad wird nicht manuell geloescht, um denselben Lauf erneut zu
  starten.
- S1-EA6 wird unter keinen Umstaenden wiederholt.

## Noch offene Freigabepunkte

```text
statische_vertragspruefung       = offen
maximale_laufzeit                = offen
maximaler_arbeitsspeicher        = offen
explizite_einmallauf_autorisierung = offen
same_session_preflight           = erst unmittelbar vor einem Lauf
```

## Kleinste notwendige Korrektur

Als Naechstes wird kein weiterer Adapter implementiert. Stattdessen ist ein
kurzer unveraenderlicher Releasevertrag zu erstellen, der nur folgende
Punkte enthaelt:

1. Bestandene statische Vertragspruefung.
2. Feste maximale Laufzeit und feste maximale Speicherbelegung.
3. Ausdrueckliche Autorisierung genau eines S1-EB-Laufs.
4. Bestaetigung der bestehenden No-Retry- und No-Claim-Grenze.
5. Verpflichtender Same-session-Preflight unmittelbar vor dem Lauf.

Erst wenn alle fuenf Punkte geschlossen sind, kann der technische Vertrag als
vollstaendig vorbereitet gelten.

## Verwendete Quellen

- `S1EB_E1_UNABHAENGIGER_VERFEINERUNGSBESTAETIGUNGSVERTRAG.md`
- `S1EB2_E1_KANONISCHER_R2_R4_R8_PREFLIGHT.md`
- `S1EB4_E1_STATISCHER_BESTAETIGUNGSKETTENVERTRAG.md`
- `S1EA6_E1_KANONISCHER_VERFEINERTER_EINMALLAUF.md`
- `S1EB17_E1_STATISCHES_GESAMTFREIGABE_AUDIT.md`
- `RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md`

## Bester naechster Schritt

Den Releasevertrag mit Ressourcenobergrenzen vorbereiten und danach statisch
gegen alle gebundenen Grenzen pruefen. Bis zum bestandenen Ergebnis bleibt der
kanonische Lauf gesperrt.
