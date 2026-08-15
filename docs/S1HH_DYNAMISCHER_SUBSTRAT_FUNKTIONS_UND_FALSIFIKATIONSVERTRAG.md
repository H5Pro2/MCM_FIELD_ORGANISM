# S1-HH: Dynamischer Substrat-Funktions- und Falsifikationsvertrag

## Status

Statischer Vertrag fuer genau einen kleinen dynamischen Substratkandidaten.
Keine Gleichung, keine Parameter, keine Runtime, kein Forschungslauf und kein
Memory-, Lern-, Organismus- oder KI-Befund.

Entscheidung:

```text
ONE_DYNAMIC_THREE_STATE_RESOURCE_CANDIDATE_BOUND_NO_EQUATION
```

S1-HH folgt der fachlichen Entscheidung, Frozen-E1 ausdruecklich zu verlassen.
Der in S1-HG gestoppte Zweig bleibt geschlossen.

## Ein Kandidat

```text
D1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER
lokaler dreistufiger Kantenressourcen-Umsatz
```

D1 liegt ausschliesslich auf vorhandenen ungerichteten MCM-Kanten. An einem
Endpunkt inzidente Kanten teilen ein endliches lokales Budget. Es entstehen
weder neue Kanten noch ein globaler Zuteiler.

Die Ressource besitzt genau drei Funktionsrollen:

1. `frei`: lokal fuer Bindung an eine vorhandene Kante verfuegbar;
2. `leitend gebunden`: auf einer Kante engagiert und dort rueckwirkungsfaehig;
3. `refraktaer`: lokal erhalten, aber voruebergehend nicht erneut bindbar.

Die Gesamtmenge aus allen drei Rollen muss lokal und global bilanziert bleiben.
Aktuelle lokale Feldteilnahme darf freie Ressource leitend binden. Kontinuierlicher
lokaler Umsatz fuehrt leitende Bindung in die refraktaere Rolle. Kontinuierliche
Erholung gibt refraktaere Ressource wieder frei. Kein Transfer darf ein Label,
einen Zaehler, eine erkannte Phase, einen Reset oder ein Zielergebnis verwenden.

## Eigene Funktionsprognose

Die neue Funktion ist nicht nur ein waehrend der Probe aktualisierter Gain.
Ihre kleinste eigene Intervention lautet:

```text
identisches S und H
+ identische leitende Kantenbindung
+ identische Gesamtressource
+ unterschiedliche Aufteilung frei / refraktaer
-> unterschiedliche Kapazitaet fuer die naechste identische Bindung
```

Ein zweistufiges E1 aus nur frei und gebunden besitzt dieses Zustandspaar
nicht. D1 sagt ausserdem voraus, dass wiederholte gleiche Kontakte die leitende
Antwort abschwaechen, ein konkurrierender Kontakt auf einer benachbarten Kante
dasselbe lokale Budget belastet und eine kontaktfreie Erholung Kapazitaet fuer
spaetere Wiederverwendung freigibt.

## Pflichtgegenprognosen

| Baseline | D1 muss vorhersagen |
| --- | --- |
| Fixed Adapter / Frozen-E1 | Kein vor der Probe fixierter Adapter reproduziert gemeinsam alle Zwischenpunkte, Konkurrenz- und Erholungspunkte. |
| Leaky / Integrator | `A-B-A` weicht nach gemeinsamem Baseline-Fit von einem belastungskontrollierten `A-Pause-A` ab, wenn B dasselbe lokale Budget beansprucht. |
| dynamisches zweistufiges E1 | Bei gleicher leitender Bindung unterscheidet allein frei gegen refraktaer die naechste Bindungskapazitaet. |
| F3 / CONST-V | Ein Tausch frei gegen refraktaer wirkt bei unveraenderter raeumlicher Gesamtmenge und fester Kopplung, ohne Ressourcentransport. |
| schneller Nachhall H | Nach Angleichung oder Ablation von H bleibt die Wirkung der erhaltenen Ressourcenaufteilung messbar. |

Die Baselines werden nicht armweise passend gemacht. Ein Parametersatz pro
Baseline muss alle spaeter registrierten Arme gemeinsam erklaeren.

## Messvertrag

Vor einer Gleichung sind folgende Messrollen bindend:

- lokaler und globaler Bilanzrest fuer `frei + leitend gebunden + refraktaer`;
- leitende Antwort ueber wiederholte identische Kontakte als Abschwaechung;
- A-Probe in `A-B-A` gegen belastungskontrolliertes `A-Pause-A` als Interferenz;
- Rueckkehr in freie Ressource und Wiederbeanspruchung an einer konkurrierenden
  benachbarten Kante;
- Substrataenderung und Feldantwort an mehreren Zeitpunkten innerhalb der Probe;
- direkte S/H-angeglichene Intervention frei gegen refraktaer;
- bitgenauer Nullpfad bei ausgeschaltetem Kandidaten.

Sinkende Feldamplitude allein gilt weder als Freigabe noch als Wiederverwendung.
Beides muss im Ressourcenledger direkt sichtbar sein.

## Verwerfung

D1 wird verworfen, sobald mindestens eine der folgenden Bedingungen gilt:

- Ressource entsteht, verschwindet, wird negativ, geclippt oder nachnormiert;
- Labels, Reward, Zaehler, Phasenerkennung, Reset oder Zieltopologie werden
  benoetigt;
- gleiche Wiederholung erzeugt keine messbare Abschwaechung;
- Konkurrenz erzeugt keinen Effekt jenseits der passenden Pausenkontrolle;
- Freigabe und anschliessende Kapazitaetswiederverwendung sind nicht direkt
  messbar;
- ein einziger vor der Probe fixierter Adapter erklaert den Gesamtverlauf;
- eine registrierte Leaky-/Integratorbaseline erklaert alle Pflichtprofile;
- F3 oder CONST-V erklaert Profile und direkte Ressourceninterventionen;
- der Effekt verschwindet nach H-Angleichung trotz erhaltener D1-Aufteilung;
- frei gegen refraktaer aendert die naechste Bindungskapazitaet nicht.

Ein Negativbefund fuehrt nicht zu nachtraeglicher Parameter- oder
Funktionskorrektur innerhalb desselben registrierten Versuchs.

## Gesperrte Claims

D1 ist eine bewusst konstruierte, bekannte technische Materialfunktion. Selbst
bei bestandenen Tests waere nur ein begrenzter dynamischer Substrateffekt
gezeigt. Gesperrt bleiben insbesondere Memory, Lernen, Engramm,
Rekonstruktion, Semantik, innerer Kontext, Organisation, Selbstregulation,
neues Naturgesetz, Organismus und KI.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1hh_function_falsification_contract.py
tests/test_dynamic_substrate_s1hh_function_falsification_contract.py
```

Der Vertrag bindet den S1-HG-Auditdigest, genau einen Kandidaten, seine drei
Ressourcenrollen, fuenf Baselinegruppen, sieben Messrollen, zehn
Verwerfungsbedingungen und die gesperrten Claims manipulationssensitiv.

## Bester naechster Schritt

S1-HI darf ausschliesslich die kleinste diskrete Ressourcenanatomie und die
exakte lokale Erhaltungsidentitaet fuer D1 binden. Noch keine Transfergleichung,
keine Rate, keine Runtime und kein Lauf. Dabei muss insbesondere gezeigt werden,
dass `refraktaer` kein umbenannter schneller Nachhall und kein zweiter frei
waehlbarer Gain ist.
