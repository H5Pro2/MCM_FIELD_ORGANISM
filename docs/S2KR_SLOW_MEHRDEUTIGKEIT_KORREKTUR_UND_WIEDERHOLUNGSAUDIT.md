# S2-KR - Korrektur und Wiederholungsaudit der Slow-Mehrdeutigkeit

## Status und Grenze

`S2KR_STATIC_SLOW_AMBIGUITY_CORRECTION_CONFIRMED`

S2-KR korrigiert ausschliesslich die Bildungsgeschichte fuer den
`B_STABLE_INTERNAL_AMBIGUITY`-Fall in S2-KQ. Die bisherige achtstufige
Geschichte liess S0 und S1 gleichzeitig in B4 und Fast zurueck. Dadurch war
die abschliessende Enthaltung nicht eindeutig der Slow-Bank zuzuordnen.

Die korrigierte Geschichte lautet:

```text
S0 S0 S0 S0 S1 S1 S1 S1 D1 D2 D3 D4 D5 D6 D7 D8 D9
```

S2-KR ist ein fokussierter statischer Wiederholungsaudit. Es wurden keine
Fixtures implementiert, keine Module importiert und keine Rezeptor-,
Memory-, Probe-, Kontext- oder Feldfunktion ausgefuehrt. Alle anderen
S2-KQ-Faelle und die Obergrenze von 800 Wertvergleichen pro Funktionsarm
bleiben unveraendert.

## Gebundener Ausgangsstand

Technischer Ausgangsstand vor der Korrektur ist Commit
`751f3e8258978a6aaa2682726dd5f8ab4555ecab`.

| Rolle | Quelle | SHA-256 vor S2-KR |
| --- | --- | --- |
| S2-KQ-Vertrag | `docs/S2KQ_READ_ONLY_TEILHINWEISABRUF_336_VERTRAG.md` | `a53c129bc490508f454aad7e20539e28369afb225ec302c660f0c81fa1c2c959` |
| Default-Live-Profil | `tools/_s2jw_default_live_profile.py` | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1-Kern | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| reale D1-D9-Fixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |

Verbindliche unveraenderte Parameter sind B4-Kapazitaet 9, Fast-Kapazitaet
3, Fast-Ablauf nach 8 Expositionen, gemeinsames Fast-Matching mit auditiver
und visueller Schwelle 0.2, visuelles PPB-Matching 0.01 und Slow-Stabilitaet
ab Support 3.

## S0- und S1-Bildung

S0 und S1 sind auf den beobachteten visuellen Positionen `0..31`
identisch. Auf allen maskierten Positionen `32..287` unterscheiden sie sich
um den vollen Rezeptorbereich. Daher gilt:

```text
d_visual(S0, S1) = 256 / 288 = 8/9
8/9 > 0.2
8/9 > 0.01
```

S0 und S1 bilden getrennte Fast-Slots und getrennte visuelle
Slow-Prototypen. Je vier identische Expositionen erzeugen drei PPB-Aufrufe:

| Schritte | Zustand | Fast-Support nach Schritt 4/8 | PPB-Aufrufe | Slow-Support | stabil |
| --- | --- | ---: | ---: | ---: | --- |
| 1-4 | S0 | 4 | 3 | 3 | ja |
| 5-8 | S1 | 4 | 3 | 3 | ja |

Die homogenen Updates veraendern die S0- und S1-Prototypwerte nicht. Beide
bleiben auf `0..31` exakt gleich und unterscheiden sich nur maskiert.

## Druckphase D1-D9

Die neun gebundenen S2-JX-Distraktoren besitzen untereinander visuelle
Abstaende von mindestens `13/24`, also groesser als die Fast-Schwelle 0.2.
Gegen die auf den beobachteten Positionen nullwertigen S0-/S1-Muster
enthaelt jeder D-Zustand mindestens einen sichtbaren aktiven Carrier.

Damit gilt fuer jeden Schritt 9 bis 17:

- kein D-Zustand aktualisiert den S0- oder S1-Fast-Slot;
- kein D-Zustand aktualisiert einen vorherigen D-Fast-Slot;
- jeder D-Zustand wird als neuer beziehungsweise ersetzender Fast-Inhalt
  angelegt;
- `consolidation_eligible` bleibt falsch;
- es entsteht kein PPB-Aufruf und kein neuer Slow-Prototyp.

Die Slow-Bank bleibt waehrend der gesamten Druckphase unveraendert bei
genau S0 Support 3 und S1 Support 3.

## Fast-Ersetzung und B4-FIFO

S0 wird zuletzt in Schritt 4, S1 zuletzt in Schritt 8 ausgewaehlt. Nach D1
in Schritt 9 sind alle drei Fast-Slots mit S0, S1 und D1 belegt. Weil D2
und D3 keine Treffer sind, greift danach die unveraenderte LRU-Ersetzung:

| Formation | statisches Fast-Ereignis |
| ---: | --- |
| 9 (`D1`) | dritter freie Slot wird `FAST_CREATED` |
| 10 (`D2`) | S0 mit `last_selected_step = 4` wird `FAST_REPLACED` |
| 11 (`D3`) | S1 mit `last_selected_step = 8` wird `FAST_REPLACED` |
| 17 (`D9`) | weder S0 noch S1 ist in Fast vorhanden |

S0 und S1 werden damit vor ihren theoretischen Ablaufpunkten durch
Kapazitaetsdruck ersetzt. Der Ablaufparameter bleibt unveraendert und muss
weiterhin validiert werden; fuer diese konkrete Geschichte ist die
tatsaechliche Verlustart jedoch LRU-Ersetzung, nicht Ablauf.

B4 behaelt nach 17 akzeptierten Formationen exakt die Indizes 9 bis 17.
Sein finaler Inhalt lautet daher vollstaendig:

```text
D1 D2 D3 D4 D5 D6 D7 D8 D9
```

S0 und S1 sind aus B4 vollstaendig FIFO-verdraengt. Die finalen hoechstens
drei Fast-Slots enthalten ausschliesslich D-Zustaende.

## Vollstaendiger Teilhinweisscan

Die strikt spaetere maskierte S0-Probe verwendet dieselbe unabhaengige
32/256-Maske wie S2-KQ. Alle drei Bankscans muessen unabhaengig von
Zwischenergebnissen vollstaendig beendet werden:

| Scan | geprueftes Inventar | Treffer | Befund |
| --- | ---: | ---: | --- |
| B4 | 9 D-Slots | 0 | `BANK_NO_OBSERVED_MATCH` |
| Fast | hoechstens 3 D-Slots | 0 | `BANK_NO_OBSERVED_MATCH` |
| visuelles Slow | S0 und S1, beide Support 3 | 2 | `BANK_MULTIPLE_OBSERVED_MATCHES` |

Aus den ersten beiden abgeschlossenen Scans entsteht
`A_RECENT_NOT_APPLICABLE`. Der Slow-Scan erzeugt
`B_STABLE_INTERNAL_AMBIGUITY`. Erst nach diesen drei Befunden darf die
oeffentliche Entscheidung `ABSTAIN_INTERNAL_AMBIGUITY` entstehen.

Ein vorzeitiger Abbruch nach dem A-Befund ist vertragswidrig. Insbesondere
darf `A_RECENT_NOT_APPLICABLE` weder als Endentscheidung noch als Ersatz
fuer den doppelten Slow-Treffer verwendet werden.

## Budgetkorrektur

Nur der Bildungsvorlauf dieses Erreichbarkeitsfalls aendert sich:

| Ressource | vorher | korrigiert |
| --- | ---: | ---: |
| Formationen im Slow-Mehrdeutigkeitsfall | 8 | 17 |
| zusaetzliche Druckformationen | 0 | 9 |
| Teilhinweisproben | 1 | 1 |
| gescannte B4-/Fast-/Slow-Slots | `9/3/4` | `9/3/4` |
| beobachtete Scanvergleiche | 512 | 512 |
| maximales Gesamtvergleichsbudget pro Arm | 800 | 800 |

Die zusaetzlichen Formationen gehoeren nur zu einem spaeter getrennt
freizugebenden realen Funktionslauf. Sie veraendern weder die read-only
Funktions- noch die Baselinegrenze.

## Wiederholungsaudit und Stoppregeln

Der fokussierte statische Wiederholungsaudit ist bestanden:

- S0 und S1 fehlen final vollstaendig in B4 und Fast;
- D1-D9 verursachen keinen PPB-Aufruf;
- beide Slow-Prototypen bleiben stabil mit Support 3;
- die maskierte Probe besitzt null A-Treffer und genau zwei B-Treffer;
- alle drei Scans muessen vor der Entscheidung abgeschlossen sein;
- die Vergleichsobergrenze bleibt 800 pro Funktionsarm.

S2-KR waere fachlich falsifiziert, wenn ein D-Zustand einen Fast-Treffer
oder PPB-Schritt ausloest, S0/S1 final noch in A vorhanden sind, ein dritter
stabiler Slow-Prototyp entsteht, einer der beiden Slow-Treffer fehlt oder
die Funktion vor Abschluss aller drei Scans entscheidet.

Quellen-, Zeit-, Slot-, Support-, Digest- oder Read-only-Bruch waere
dagegen `NOT_EVALUABLE` und kein regulaerer Funktionsbefund.

## Ergebnis und naechste Grenze

Die korrigierte 17-Schritt-Geschichte isoliert die Slow-Mehrdeutigkeit
eindeutig. Der vorherige Acht-Schritt-Fall bleibt als erkannte statische
Materialisierungsluecke dokumentiert und darf nicht ausgefuehrt werden.

Nach S2-KR ist die kleine private read-only Slotscan-/A-Projektionsfunktion
mit unabhaengiger Direktbaseline und fokussierten neutralen Tests fachlich
implementierbar. Ein realer Teilhinweis-Funktionslauf bleibt separat
freizugeben; neue Runner- oder Recorderinfrastruktur ist nicht begruendet.
