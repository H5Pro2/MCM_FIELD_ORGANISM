# S1-IF: Statischer DTS-1 Abschwaechungsvertrag

## Status

S1-IF bindet ausschliesslich die kleinste Abschwaechungspruefung unter
wiederholtem identischem lokalem Kontakt. Es wird keine Gleichung eingefuehrt,
kein Kontaktzaehler oder Fixturewert gewaehlt, kein Harness implementiert und
kein Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_REPEATED_EQUAL_CONTACT_ATTENUATION_CONTRACT_BOUND
```

Vertragsdigest:

```text
bfad62c3da8abf8a7cf6777adb401b33b35135360bd566093631de124cd47f56
```

## Quellen

Der Vertrag bindet:

- S1-HH mit Digest
  `5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388`;
- den bestandenen technischen S1-IE-Audit mit Receipt
  `dbaa141450f1a00defb71824feb4e61bbef727c0023ea1d1e19cc979581ebcea`.

S1-IE ist nur die technische Voraussetzung fuer einen kausalen Feldreadout.
Es liefert selbst noch keinen Abschwaechungsbefund.

## Kontaktfolge

Eine einzelne bestehende isolierte Kante erhaelt mindestens drei unmittelbar
aufeinanderfolgende A-Kontakte. Die naechste Stufe muss deren genaue endliche
Zahl vorab festlegen. Gleich bleiben positive lokale Beteiligung, Dauer,
Kontaktform und Ereignisgrenzen.

Nur die vollstaendige gueltige DTS-1-Anatomie wird von A-Kontakt zu A-Kontakt
weitergetragen. Sie darf nicht zurueckgesetzt werden. Kontaktindex, Armname,
Ergebnis oder Zukunftszustand duerfen keinen Transfer steuern.

Jeder Feldreadout verwendet denselben vorregistrierten S/H-Pruefvorzustand.
Der Pruefreadout wird nicht in die Kontaktfolge zurueckgeschrieben. Damit kann
eine gewoehnliche fortlaufende S/H-Integration nicht als Ressourcenwirkung
gezaehlt werden.

## Direkte Messrollen

An jedem Kontakt werden gemeinsam gebunden:

- vollstaendige Anatomie vor und nach dem Kontakt;
- akzeptierte Bindung, Umsatz und Erholung aus dem direkten Transferledger;
- lokale und globale Ressourcenbilanz;
- angewandter Adapter und vollstaendiger S/H-Ausgang des gemeinsamen
  Pruefreadouts;
- orientierter S-Kontrast der Zielkante;
- derselbe Readout bei angeglichenem oder abgetragenem H.

Die spaetere gerichtete Prognose muss sowohl eine strikt sinkende akzeptierte
Bindung als auch die dazu vorab gerichtete Abschwaechung des gemeinsamen
Feldreadouts fordern. Keine der beiden Messrollen darf die andere ersetzen.
Richtung, Checkpoints, Nichtnullmarge und Float64-Grenze muessen vor jeder
Ausfuehrung analytisch feststehen.

## Kontrollen

1. Wertidentische vollstaendige Eingaben liefern bitgenau identische Ledger,
   Adapter und Feldausgaenge.
2. A0 liefert an jedem Checkpoint bitgenau den neutralen Feldpfad.
3. Ein vor der Folge fixierter Adapter erhaelt weder Kontaktindex noch die
   veraenderte DTS-1-Anatomie.
4. Die gerichtete Feldabschwaechung muss bei wertidentischem oder abgetragenem
   H bestehen bleiben.
5. Beteiligung null liefert exakt null akzeptierte Bindung und keinen
   kontaktbedingten Feldclaim.

## Gegenbaselines

| Baseline | Gebundene Gegenprognose |
| --- | --- |
| Fixed Adapter / Frozen-E1 | Ein vor der Folge fixierter Adapter verwendet bei jedem identischen Pruefzustand dieselbe Kopplung. |
| Leaky / Integrator | Identische S/H-Pruefvorzustaende tragen keinen fortgeschriebenen Feldzustand und besitzen kein Drei-Rollen-Ressourcenledger. |
| dynamisches zweistufiges E1 | Abschwaechung allein ist nicht unterscheidend. Der S1-IB-Eingriff frei gegen refraktaer und der S1-IE-Feldreadout bleiben gemeinsam erforderlich. |
| F3 / CONST-V | Ohne lokalen Drei-Rollen-Umsatz fehlt das direkte Bindungs- und Refraktaerledger der Kontaktfolge. |
| schneller Nachhall | Angeglichenes oder abgetragenes H darf die gerichtete Readoutfolge nicht aufheben. |

Keine Baseline darf Kontaktindex, verborgene Ressourcenzustaende, Armnamen
oder einen separaten Fit je Checkpoint erhalten.

## PASS und STOPP

Ein spaeterer PASS verlangt atomar die vollstaendige aktive Folge, alle fuenf
Kontrollen, beide vorregistrierten strikten Richtungen, den H-kontrollierten
Readout oberhalb seiner festen Grenze sowie gueltige Anatomien, Bilanzen und
Feldbereiche.

STOPP gilt bei ungleichen Kontakten oder Pruefzustaenden, Ressourcenreset,
Zaehler oder Phasenerkennung, fehlender Richtung in direktem Ledger oder
Feldreadout, Scheitern der H-Kontrolle, Bilanzverletzung, Baselineerweiterung,
ergebnisabhaengiger Nachwahl oder nicht registrierter Ausfuehrung. Ein
Teil-PASS ist ausgeschlossen.

## Aussagegrenze

S1-IF bindet nur Funktion, Messung und Falsifikation. Abschwaechung wurde noch
nicht ausgefuehrt oder nachgewiesen. Insbesondere sind Interferenz,
Kapazitaetsfreigabe, Wiederbeanspruchung, Materialeignung und eine
Nichtreduzierbarkeit auf dynamisches E1 offen. Weitergehende Claims bleiben
gesperrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1if_attenuation_contract.py
tests/test_dynamic_substrate_s1if_attenuation_contract.py
```

Acht Tests pruefen Quellenbindung, gleiche Kontakte, kontinuierliche Anatomie,
direkte Messrollen, fuenf Kontrollen, alle Gegenbaselinegruppen, atomare
STOPP-Regeln, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IG darf ausschliesslich ein endliches synthetisches Fixture und einen
Ausfuehrungsvertrag fuer S1-IF binden. Vor jeder Implementierung muessen die
exakte Kontaktzahl, gueltige Startanatomie, gemeinsame Beteiligung und
Prueffelder, Kontakt- und Readoutzeiten, analytische Ledger- und
Feldrichtungen, Rundungsgrenze, Fallmatrix und maximales technisches
Schrittbudget feststehen. Noch keine Implementierung, Runtime oder
Ausfuehrung.
