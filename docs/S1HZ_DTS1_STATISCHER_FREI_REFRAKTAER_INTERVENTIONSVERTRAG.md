# S1-HZ: Statischer DTS-1 Frei/Refraktaer-Interventionsvertrag

## Status

S1-HZ bindet die kleinste eigene Zustandsgegenprognose des DTS-1-Kandidaten.
Es wird keine neue Gleichung eingefuehrt, kein Parameterwert gewaehlt, kein
Executor implementiert und kein Schritt ausgefuehrt.

Entscheidung:

```text
DTS1_FREE_REFRACTORY_INTERVENTION_CONTRACT_BOUND
```

Vertragsdigest:

```text
968a0ed6e033da839fae767cbf2a5ed2129440a6ab9c68c386fe206c606cff57
```

## Quellen

Der Vertrag bindet gleichzeitig:

- den S1-HH-Funktions- und Falsifikationsvertrag mit Digest
  `5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388`;
- den bestandenen technischen S1-HY-Audit mit Receipt
  `c6f75a0a1009c51dd03ad546ae04c4aded34ecf7ccd0b687bcbac4d715f24de2`.

S1-HY wird dabei nur als technische Voraussetzung gelesen. Sein PASS ist
kein Funktionsbefund.

## Interventionspaar

Genau zwei Arme sind zulaessig:

```text
F_HIGH: mehr freie, weniger refraktaere Ressource
R_HIGH: weniger freie, mehr refraktaere Ressource
```

Beide Arme verwenden dieselbe einzelne bestehende Kante. Identisch bleiben:

- Endpunktidentitaeten und positive Kapazitaeten;
- Gesamtressource und leitend gebundene Ressource;
- `S` und `H` an beiden Endpunkten;
- positive aktuelle Feldbeteiligung;
- positive Schrittdauer und dieselben vorhandenen DTS-1-Raten;
- Kontakt, Konfiguration und Ereignisgrenze, falls spaeter der gekoppelte
  Wrapper verwendet wird.

Nur die Aufteilung frei/refraktaer darf variieren. In `R_HIGH` wird eine
positive, spaeter fest zu bindende Menge aus frei nach refraktaer verschoben.
Freie Ressource bleibt aus dem S1-HI-Halbanteilsledger abgeleitet. Sie darf
weder separat gespeichert noch geschrieben oder nachnormiert werden.

Die isolierte Einzelkante verhindert, dass eine benachbarte Kante das lokale
Budget waehrend dieser kleinsten Intervention beansprucht. Beide Arme muessen
gueltige, nichtsaturierte innere Zustaende sein.

## Direkte Messgroesse

Primaere Messgroesse ist ausschliesslich die im bestehenden passiven
S1-HP-Transferledger ausgewiesene akzeptierte Bindungsmenge `engagement` der
Zielkante. Sie wird fuer zwei Vorschlaege aus abgeschlossenen Vorzustaenden vor
dem atomaren Commit verglichen.

Die eigene Gegenprognose lautet:

```text
engagement(F_HIGH) > engagement(R_HIGH)
```

Nettoaenderung der Bindung, Umsatz, Erholung und Feldamplitude duerfen diese
Messgroesse nicht ersetzen. Beide vollstaendigen Eingangs- und
Ergebnisanatomien muessen die lokalen und globalen Ressourcenbilanzen halten.

## Nullkontrollen

1. Zwei wertidentische Aufteilungen liefern bitgenau dasselbe vollstaendige
   Transferledger.
2. Bei Beteiligung null ist die akzeptierte Bindungsmenge in beiden
   Aufteilungen exakt null.
3. Bei Bindungsrate null ist die akzeptierte Bindungsmenge in beiden
   Aufteilungen exakt null.

## Gegenbaselines

| Baseline | Gebundene Gegenprognose |
| --- | --- |
| Fixed Adapter / Frozen-E1 | Gleiches `S`, `H` und gleiche leitende Bindung ergeben denselben aktuellen Adapter; ein Frei/Refraktaer-Zustand fuer die naechste Bindung fehlt. |
| Leaky / Integrator | Bei gleichem `S`, `H`, Eingang und Schritt fehlt die intervenierte Zustandskoordinate. |
| dynamisches zweistufiges E1 | Gleiche leitende Bindung und Gesamtressource kollabieren beide Arme auf denselben zweistufigen Zustand. |
| F3 / CONST-V | Bei gleicher raeumlicher Gesamtmenge und ohne Transport fehlt ein lokales Frei/Refraktaer-Bindungsledger. |
| schneller Nachhall | Exakt gleiches `H` kann die beiden Ressourcenaufteilungen nicht unterscheiden. |

Keine Baseline darf nachtraeglich den Armnamen oder die verborgene
Frei/Refraktaer-Koordinate erhalten. Eine solche Erweiterung waere ein neues
Modell und keine Gegenbaseline.

## PASS und STOPP

Ein spaeterer Audit darf nur atomar PASS liefern, wenn beide Interventionsarme,
alle drei Nullkontrollen, alle Bilanzen, die strikte gerichtete Differenz und
alle fuenf Zustandsraum-Gegenprognosen bestehen.

STOPP gilt insbesondere bei ungleichen Kontrollgroessen, ungueltiger oder
saturierter Anatomie, fehlender strikter Engagement-Differenz, nicht exakter
Nullkontrolle, Proxy-Messung, versteckter Baseline-Erweiterung, nachtraeglicher
Anpassung oder nicht registrierter Ausfuehrung. Teil-PASS ist ausgeschlossen.

## Aussagegrenze

S1-HZ hat nur einen statischen Interventionsvertrag gebunden. Es wurde weder
eine Ressourcenwirkung noch eine Feldfunktion gemessen. Abschwaechung,
Interferenz, Kapazitaetsfreigabe, Wiederbeanspruchung und Materialeignung
bleiben offen. Weitergehende Projektclaims bleiben gesperrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1hz_free_refractory_intervention_contract.py
tests/test_dynamic_substrate_s1hz_free_refractory_intervention_contract.py
```

Neun Tests pruefen Quellenbindung, Paarinvarianten, abgeleitete freie
Ressource, direkte Messgroesse, Nullkontrollen, alle Gegenbaselines,
Atomaritaet, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IA darf ausschliesslich ein endliches synthetisches Fixture und einen
Ausfuehrungsvertrag fuer diese bereits gebundene Intervention festlegen. Vor
einer Implementierung muessen konkrete innere, nichtsaturierte Armwerte, ein
technisches Schrittlimit, die exakte Ausgabestruktur und ein Rundungs- oder
Exaktheitskriterium vorregistriert werden. Noch keine Implementierung,
Runtimeintegration oder Ausfuehrung.
