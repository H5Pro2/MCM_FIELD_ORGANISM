# Z2-B: Kollisionsaudit lokaler Feldarbeit und lokalen Flussdurchgangs

Stand: 2026-08-06

Entscheidung: `NO_ADMISSIBLE_EVENT_ORDER_SOURCE`

Status:

- rein statischer Audit der bestehenden Feld- und Materialvertraege;
- keine neue Energie-, Arbeits-, Fluss- oder Zeitvariable;
- keine Implementierung, Ausfuehrung oder neuer Forschungslauf;
- Z2 ist fuer die aktuelle Runtime abgeschlossen.

## Forschungsfrage

Besitzt die aktuelle MCM-Runtime in signierter lokaler Feldarbeit oder lokalem
Flussdurchgang einen eigenstaendigen physikalischen Bilanztraeger, der eine
ereignisgetragene Entwicklungsordnung begruenden kann, ohne nur momentanen
Feldzustand, Weltzeitintegral, Pfadlaenge oder vorgegebene Materialantwort zu
sein?

## Bestehender schneller Feldfluss

Auf einer gerichteten lokalen Kante gilt fuer die neutrale Diffusion:

```text
J(j -> i) = r * (S_j - S_i)
r = 1 / response_time_seconds
```

Der momentane Fluss ist damit vollstaendig aus S, fester Nachbarschaft und
fester Reaktionsrate bestimmt. Der vorhandene passive Nullaudit bestaetigt:

- Kantenantisymmetrie;
- Gleichheit von lokaler Divergenz und Diffusionsgenerator;
- verschwindende Gesamtdifferenz in der geschlossenen Feldanatomie;
- identische Fluesse bei angeglichenem schnellen Feld;
- keine Akkumulation und keine Rueckschreibung.

Der momentane Fluss ist eine reale lokale Ursache innerhalb der Simulation,
aber kein weiterer Zustand und keine unabhaengige Geschichte.

## Quadratische Diffusionsarbeit

Die naheliegende konjugierte Differenz ist erneut `S_j - S_i`. Das Produkt
aus Fluss und Differenz ergibt bis zur Vorzeichenkonvention:

```text
P_ij = J(j -> i) * (S_j - S_i)
     = r * (S_j - S_i)^2
```

Diese Groesse ist die bereits bekannte nichtnegative
Diffusionsdissipation. Sie fuegt dem momentanen Feld keine Information hinzu.
Ihre Summe prueft die Passivitaetsbilanz der vorhandenen S-Dynamik, waehlt
aber weder eine neue Zustandsrolle noch deren spaetere Rueckwirkung aus.

Die quadratische Speicherfunktion

```text
E_S = 1/2 * S^T S
```

ist ebenfalls eine Funktion des aktuellen S-Zustands. Sie ist keine
gesonderte gespeicherte physische Energie und keine Entwicklungsordnung.

## Signierte Feldarbeit

Eine echte Arbeitsform benoetigt ein physikalisch begruendetes konjugiertes
Paar, beispielsweise Kraft und Verschiebung, Potential und Ladung oder
Spannung und Dehnung. Der aktuelle MCM-Vertrag liefert dafuer nicht genug:

- Aktivierung besitzt keine physikalisch kalibrierte Energieeinheit;
- es gibt keine unabhaengige lokale Verschiebungs- oder Stoffkoordinate;
- Feldfluss besitzt keine hergeleitete Materialpolaritaet;
- eine Umrechnung in Materialbewegung oder gespeicherte Arbeit hat keine
  hergeleitete Skala;
- es gibt keine unabhaengige Messung von Speicherung und Dissipation.

Eine Definition wie

```text
W_i(t) = Integral phi(S, J, Kontakt) dt
```

setzt daher erst fest, welche Groesse als Leistung gilt und wie sie
akkumuliert wird. `W_i` waere ein neuer Integratorzustand. Mit Leck wird er
zur Leaky-Spur, mit Saettigung zum begrenzten Integrator und mit
zustandsabhaengigem Lesen zur adaptiven oder hysteretischen Kennlinie.

## Lokaler Flussdurchgang

Fuer eine Kante waeren zwei direkte Formen denkbar:

```text
Q_ij = Integral J_ij dt
A_ij = Integral |J_ij| dt
```

`Q_ij` ist ein signierter Durchgangsakkumulator. In einer lokalen Bilanz ist
seine Divergenz bereits an Zustandsaenderung und andere Kantenfluesse
gebunden; einzelne Kantenwerte speichern zusaetzlich die gewaehlte
Pfadzerlegung. `A_ij` ist eine monotone Pfadlaenge, verliert das Vorzeichen
und waechst auch bei reversibler Hin-und-zurueck-Bewegung.

Beide Formen benoetigen einen neuen akkumulierten Zustand. Keine der beiden
liefert aus sich selbst:

- eine endliche Kapazitaet;
- eine physisch bestimmte Rueckwirkung;
- funktionale Loesung durch weitere Feldgeschichte;
- andere Wiederpraegung derselben Kapazitaet;
- eine Abgrenzung gegen Integrator und Hysterese.

## F3-Medium M

M besitzt bereits eine lokale, begrenzte und umverteilte Zustandsrolle. Sein
Kantenfluss wird jedoch mit `lambda_sm_per_second` aus S und M berechnet. M
ist deshalb Teil der in Lauf 196 nachgewiesenen weltzeitgebundenen Dynamik.

Eine kumulierte F3-Kantenmenge waere nicht M selbst, sondern ein neuer
Durchgangsobserver. Die Rueckwirkung der aktuellen F3-Runtime ist bereits an
`dM/dt` gebunden. Eine zusaetzliche Wirkung aus kumuliertem Durchgang muesste
neu festlegen, wie Pfadgeschichte gelesen, begrenzt und geloest wird.

## Kollision mit vorhandenen Befunden

| vorgeschlagene Rolle | bestehende Reduktion oder fehlende Festlegung |
| --- | --- |
| momentaner S-Kantenfluss | exakt aus S, Anatomie und Reaktionsrate rekonstruierbar |
| quadratische lokale Leistung | bestehende Diffusionsdissipation und Passivitaetsbilanz |
| aktuelle quadratische Speicherfunktion | algebraische Funktion des vorhandenen S-Zustands |
| signierter Flussdurchgang | zusaetzlicher Produkt- oder Pfadintegrator |
| absoluter Flussdurchgang | lokaler Momenten- beziehungsweise Pfadlaengenintegrator |
| Feldfluss als Materialgeschwindigkeit | Polaritaet und Skala durch Feldvertrag unbestimmt |
| begrenzte akkumulierte Arbeit | Saettigungsintegrator oder adaptive Kennlinie |
| rate-unabhaengige Arbeitsschleife | neue Hysterese- oder Duhem-Konstitution erforderlich |
| konservierter Arbeitsstoff | neue Stoffrolle, Mobilitaet und Energielandschaft erforderlich |
| dissipativer Arbeitszustand | feste Relaxation oder K1-Leaky-/Rekurrenzbaseline |

Der fruehere kontrafaktische Transportaudit ist fuer die Entscheidung
besonders scharf: Zwei entgegengesetzte Abbildungen desselben signierten
Feldflusses sind bilanziell und kinematisch zulaessig, erzeugen aber
unterschiedliche Morphologien. Der aktuelle Feldvertrag bestimmt weder ihre
Polaritaet noch ihre Skala. Eine Energiebeschriftung beseitigt diese
Unterbestimmtheit nicht.

## Z2-Entscheidung

`NO_ADMISSIBLE_EVENT_ORDER_SOURCE`

Nach Abzug von momentaner Zustandsableitung, Passivitaetsobserver,
Weltzeitintegral, Pfadlaenge, Materialzaehler, Hysterese und fester Rekurrenz
bleibt in der aktuellen Runtime kein unabhaengiger lokaler Bilanztraeger fuer
eine ereignisgetragene Entwicklungsordnung uebrig.

Damit sind Z2-A und Z2-B abgeschlossen. Z2-C endet ohne Freigabe einer neuen
Zustandsrolle, Gleichung oder Implementierung.

Diese Entscheidung ist kein Unmoeglichkeitsbeweis fuer relative Feldzeit
oder ein digitales MCM-Entwicklungssubstrat. Sie begrenzt die Herleitung:
Eine neue Rolle kann nicht als bereits verborgene Eigenschaft des aktuellen
S/H/M-Flusses ausgegeben werden. Sie muss als neue, offen deklarierte
physikalische Forschungsannahme eingefuehrt und gegen alle genannten
Baselines geprueft werden.

## Verwendete Projektquellen

- [Z2-Zulassigkeitsaudit](Z2_ZULASSIGKEITSAUDIT_LOKALE_EREIGNISGETRAGENE_ENTWICKLUNGSORDNUNG.md)
- [Z2-A-Bestandsaudit](Z2A_BESTANDSAUDIT_S_H_M_ZEITDIMENSIONEN_UND_REPARAMETRISIERUNG.md)
- [Passivitaet, Feldarbeit und Ende der Substratherleitung](architektur/069_PASSIVITAET_FELDARBEIT_UND_ENDE_DER_SUBSTRATHERLEITUNG.md)
- [Abgrenzung direkter radialer Flussursachen](architektur/085_ABGRENZUNG_DIREKTER_RADIALER_FLUSSURSACHEN.md)
- [Kontrafaktische Feldfluss-Transportgrenze](architektur/086_KONTRAFAKTISCHE_FELDFLUSS_TRANSPORTGRENZE.md)
- [H2-Bestandsaudit](H2_BEGRenztes_UMVERTEILBARES_FELDMEDIUM_BESTANDSAUDIT.md)
- [H2-B-Materialklassenvergleich](H2B_VERGLEICH_PASSIVER_MATERIALKLASSEN.md)
- [H3-Quellenaudit](H3_LOKALE_RELATIONSABHAENGIGE_MATERIALANTWORT_QUELLENAUDIT.md)
- [K1-Konstitutiver Schliessungsaudit](K1_KONSTITUTIVER_SCHLIESSUNGSAUDIT.md)
- [Lauf 196](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md)
- Runtime: `mcm_field_organism/instantaneous_field_flow_null_probe.py`
- Runtime: `mcm_field_organism/signed_field_flow_transport_counterfactual.py`
- Runtime: `mcm_field_organism/mcm_f3_coupling.py`
- Runtime: `mcm_field_organism/mcm_f3_runtime.py`

## Aussagegrenze

Der Audit weist weder Feldzeit noch Memory, Organisation, Topologie, inneren
Kontext, Semantik, Selbstregulation oder KI nach. Er bewertet keine neue
Materialgleichung, weil keine eingefuehrt wurde.

## Bester naechster Schritt

Die automatische Herleitung einer Entwicklungsordnung aus der aktuellen
Runtime bleibt beendet. Der
[Z3-Hypothesenvertrag lokaler konstitutiver Deformation](Z3_HYPOTHESENVERTRAG_LOKALE_KONSTITUTIVE_DEFORMATION.md)
bindet inzwischen genau eine neue Rollenklasse fuer einen statischen Quellen-
und Reduktionsaudit. Noch ist keine konkrete Gleichung oder Implementierung
zugelassen.
