# Z2-A: Bestandsaudit der S-, H- und M-Zeitdimensionen

Stand: 2026-08-06

Entscheidung: `NO_EXISTING_STATE_REPARAMETERIZATION`

Status:

- rein statischer Audit der aktuellen Runtime;
- keine neue Variable, Gleichung oder Mechanik;
- keine Implementierung, Ausfuehrung oder neuer Forschungslauf;
- Lauf 196 bleibt der letzte ausgefuehrte Forschungslauf;
- der anschliessende Z2-B-Audit ist inzwischen ebenfalls abgeschlossen.

## Forschungsfrage

Enthaelt einer der vorhandenen Zustaende S, H oder M bereits ein lokales
Inkrement, das die weitere Entwicklung unabhaengig von Weltsekunden ordnen
kann, oder waere eine solche Verwendung nur eine algebraische
Reparametrisierung derselben weltzeitgebundenen Dynamik?

## Rekonstruktion des aktuellen Zeitvertrags

Die aktuelle Runtime besitzt genau eine Integrationszeit: die in Sekunden
gemessene Dauer `MCMFieldStepTime.elapsed_seconds`. Alle vorhandenen
Zustandsrollen werden durch diese Dauer fortgeschrieben.

| Rolle | aktuelle Dynamik | Zeitbindung |
| --- | --- | --- |
| schnelles Feld S | Diffusion beziehungsweise lokale Antwort mit Rate `1 / response_time_seconds`, optionaler Leckrate und F3-Rueckwirkung | pro Weltsekunde |
| Nachhall H | Annaeherung an S mit Rate `1 / time_constant_seconds`, optional plus Leckrate | pro Weltsekunde |
| F3-Medium M | lokale Kantenfluesse mit `lambda_sm_per_second`; Rueckwirkung ist an `dM/dt` gebunden | pro Weltsekunde |
| Rezeptorkontakt | Kontaktuebernahme mit Retention `exp(-read_duration / response_time_seconds)` | reale Lesedauer in Sekunden |
| B3-Pflichtbaseline | lineare gekoppelte Zustandsrate und Rueckwirkung mit denselben Zeitdimensionen | pro Weltsekunde |
| numerische Integration | exakte Exponentialentwicklung oder SSPRK33 mit `elapsed_seconds` beziehungsweise Teilintervallen | Weltsekunden als Integrationsparameter |

In abstrakter kontaktfreier Form gilt damit:

```text
dS/dt = (1/tau_S) L_G S - leak_S S + R_F3
dH/dt = (1/tau_H) (S - H) - leak_H H
dM/dt = lokaler Kantenfluss(S, M; lambda_SM pro Sekunde)
R_F3  = lokale Funktion von S und dM/dt
```

Die genaue numerische Realisierung aendert diesen Zeitvertrag nicht. Auch die
punktweise Rezeptoraufnahme ist nicht ereigniszaehlend oder
rate-unabhaengig, weil ihre Wirkung explizit von der realen Lesedauer
abhaengt.

## Formale Reparametrisierung

Fuer den vorhandenen Gesamtzustand `X = (S, H, M)` gilt:

```text
dX/dt = F(X, u(t))
```

Eine lokale Entwicklungskoordinate `xi` mit

```text
dxi/dt = g(X, u)
```

liefert, wo `g` ungleich null ist, lediglich:

```text
dX/dxi = F(X, u) / g(X, u)
```

Solange `g` nur algebraisch aus S, H, M und aktuellem Kontakt berechnet wird,
enthaelt `xi` keine neue Zustandsinformation. Es ist ein zustandsabhaengiger
Takt beziehungsweise Gain derselben Gleichung. Wird `xi` dagegen akkumuliert
und spaeter kausal wirksam, ist es eine neue Zustandsrolle, die eigenstaendig
physikalisch begruendet und gegen Integrator-, Hysterese- und
Pfadlaengenbaselines geprueft werden muss.

## Gleichfoermige Zeitdehnung

Sei eine gedehnte Quelle `u_a(t) = u(t/a)`. Eine entsprechend nur
reparametrisierte Zustandsbahn `X_a(t) = X(t/a)` erfuellt links
`dX_a/dt = (1/a) dX/dt`, waehrend rechts die unveraenderten per-Sekunde-Raten
der Runtime stehen. Beide Seiten sind fuer `a != 1` im Allgemeinen nicht
gleich.

Kovarianz wuerde daher mindestens eine der folgenden Aenderungen verlangen:

- alle internen Raten und Kontaktlesedauern passend zum externen Quelltempo
  skalieren; das setzt unzulaessiges Wissen ueber die Welttransformation
  voraus;
- eine rate-unabhaengige konstitutive Entwicklung einfuehren; das waere eine
  neue Mechanik und keine Entdeckung in S, H oder M.

Dieser statische Befund stimmt mit Lauf 196 ueberein: Technische Teilung
aendert den Sachpfad nicht, gleichfoermige Weltzeitdehnung und -stauchung
dagegen deutlich.

## Gepruefte Bestandskandidaten

| Kandidat | Ergebnis | Grund |
| --- | --- | --- |
| Tick, Schritt oder Kontaktindex | ausgeschlossen | technischer Zaehler statt lokaler Feldphysik |
| S als lokale Uhr | keine unabhaengige Rolle | S ist Zustand der per-Sekunde-Felddynamik und nicht zwingend monoton |
| H als lokale Uhr | keine unabhaengige Rolle | H ist ein weltzeitgebundener Leaky-Nachhall und kann stationaer oder ruecklaeufig sein |
| M als lokale Uhr | keine unabhaengige Rolle | M wird mit einer Rate pro Sekunde umverteilt; lokale Werte sind nicht zwingend monoton |
| signiertes `dS` | unzureichend | akkumuliert ohne Zusatzstate nur die Endpunktdifferenz und traegt keinen unabhaengigen Verlauf |
| Betrag von `dS` oder lokale Pfadlaenge | neuer Observer oder Integrator | benoetigt Akkumulation; als reine Ableitung bleibt er vom vorhandenen RHS abgeleitet |
| momentaner lokaler Kantenfluss | keine Zusatzinformation | ist aus aktuellem Feld, Geometrie und festen Raten bestimmt; sein passiver Nullaudit ist bereits geschlossen |
| akkumulierte Feldarbeit oder Flussmenge | noch keine Bestandsrolle | benoetigt einen neuen lokalen Traeger und eine konstitutive Wirkung |
| normierte Phase oder Bogenlaenge | ausgeschlossen | benoetigt globalen Observer, Oszillator oder festgelegte Zyklusstruktur |
| adaptive Zeitkonstante oder Gain | keine neue Ordnung | veraendert die Geschwindigkeit einer weiterhin weltzeitparametrisierten Rekurrenz |

## Abgleich mit geschlossenen Klassen

- Der H3-Quellenaudit zeigt, dass lokale relationale Bestandswerte ohne
  neuen Traeger auf schnellen Feldzustand, feste Anatomie, aktuellen Kontakt
  und Weltzeitdauer reduzierbar bleiben.
- Der H2-B-Materialvergleich schliesst eine feste memristive oder
  Duhem-Hysterese als direkte Organismusmechanik, weil ihre
  Geschichtsschreibung bereits konstitutiv vorgegeben waere.
- Der K1-Schliessungsaudit grenzt feste lineare Modi, fading-memory
  Rekurrenzen sowie konservative oder dissipative Relaxation als
  Pflichtbaselines ab.
- Der passive Audit des momentanen Feldflusses belegt, dass dessen aktueller
  Wert keinen Zustand jenseits des schnellen Feldes liefert.

Z2-A darf diese Klassen nicht unter dem Namen Feldzeit erneut oeffnen.

## Entscheidung

`NO_EXISTING_STATE_REPARAMETERIZATION`

Keiner der vorhandenen Zustaende S, H oder M liefert eine unabhaengige lokale
ereignisgetragene Entwicklungsordnung. Eine rein algebraische
Reparametrisierung bleibt dieselbe Weltzeitdynamik; eine akkumulierte
Reparametrisierung waere eine neue konstitutive Zustandsrolle.

Die Entscheidung ist kein allgemeiner Beweis, dass eine solche Rolle
physikalisch unmoeglich ist. Sie besagt nur, dass sie nicht bereits verborgen
in der aktuellen S/H/M-Runtime vorliegt.

## Quellen

- [Z2-Zulassigkeitsaudit](Z2_ZULASSIGKEITSAUDIT_LOKALE_EREIGNISGETRAGENE_ENTWICKLUNGSORDNUNG.md)
- [Lauf 196](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md)
- [MINI_DIO-Zeitkontext-Reaudit](MINI_DIO_ZEITKONTEXT_REAUDIT_NACH_LAUF_194.md)
- [H2-B-Materialklassenvergleich](H2B_VERGLEICH_PASSIVER_MATERIALKLASSEN.md)
- [H3-Quellenaudit](H3_LOKALE_RELATIONSABHAENGIGE_MATERIALANTWORT_QUELLENAUDIT.md)
- [K1-Konstitutiver Schliessungsaudit](K1_KONSTITUTIVER_SCHLIESSUNGSAUDIT.md)
- Runtime: `mcm_field_organism/field_step_time.py`
- Runtime: `mcm_field_organism/neutral_local_field_substrate.py`
- Runtime: `mcm_field_organism/mcm_substrate_state.py`
- Runtime: `mcm_field_organism/mcm_f3_coupling.py`
- Runtime: `mcm_field_organism/mcm_f3_runtime.py`
- Baseline: `mcm_field_organism/mcm_f3_baseline_coupling.py`
- Bestandsaudit: `mcm_field_organism/instantaneous_field_flow_null_probe.py`

## Aussagegrenze

Dieser Audit weist weder relative Feldzeit noch Memory, Organisation,
Topologie, inneren Kontext, Semantik, Selbstregulation oder KI nach. Er gibt
keine Implementierung und keinen Versuch frei.

## Bester naechster Schritt

Der anschliessende
[Z2-B-Kollisionsaudit](Z2B_KOLLISIONSAUDIT_LOKALE_FELDARBEIT_UND_FLUSSDURCHGANG.md)
hat keinen unabhaengigen physikalischen Bilanzrest gefunden und Z2 mit
`NO_ADMISSIBLE_EVENT_ORDER_SOURCE` geschlossen. Der anschliessende
[Z3-Hypothesenvertrag](Z3_HYPOTHESENVERTRAG_LOKALE_KONSTITUTIVE_DEFORMATION.md)
laesst genau eine neue Rollenklasse fuer einen statischen Quellen- und
Reduktionsaudit zu.
