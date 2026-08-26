# S1-UI: ACM-1H private atomare Vier-Knoten-Feldintegration und synthetische Abnahme

## Freigabe und Grenze

S1-UI setzt die ausdrueckliche Freigabe fuer genau folgende Rollen um:

- einen privaten In-Memory-`ACM1HFieldCarry`;
- genau einen atomaren synchronen Vier-Knoten-Feldschritt;
- synthetische Integrations- und ACM-OFF-Regressionstests.

Nicht freigegeben und nicht umgesetzt wurden eine oeffentliche API, ein
Snapshotumbau oder ein Forschungsfeldlauf. Der produktive
`SharedMCMFieldSnapshot` und seine Wiederaufnahme bleiben unveraendert.

## Private Implementierungsgrenze

Die neue Implementierung liegt ausschliesslich in:

```text
mcm_field_organism/_acm1h_field_runtime.py
```

Das Modul wird weder aus dem Paketroot noch aus `current_api` exportiert.
Der vorhandene reine S1-UG-Kern bleibt ebenfalls privat und unveraendert.

## Privater Zustand

`ACM1HPrivateState` bindet:

```text
schema_id
configuration_digest
geometry_id
edge_inventory_digest
field_tick
field_time_endpoint
z_left
z_right
state_digest
```

Die beiden begrenzten `z`-Werte sind die einzigen neuen fortbestehenden
Zahlenwerte. Aktivierungen, Nachhall, Rezeptorkontakte, Primaerfluesse,
Motivfaktoren und Generatoren werden nicht in den privaten Zustand kopiert.

## Atomarer Feld-/Zustandscarry

`ACM1HFieldCarry` bindet genau ein vollstaendiges `SharedMCMField` und genau
einen dazugehoerigen privaten Zustand. Feld-, Zustands-, Konfigurations-,
Geometrie-, Kanteninventar- und Carrydigest werden bei Konstruktion und vor
jeder Fortschreibung erneut geprueft.

Der Carry ist kein Snapshot. Ein Feldsnapshot allein bleibt unzureichend,
um einen ACM-1H-Zustand nach Prozessende wiederaufzunehmen. S1-UI fuegt
keinen Serialisierungs- oder Restorepfad hinzu.

## Gebundene Transaktionsfolge

Ein aktiver Schritt arbeitet in dieser Reihenfolge:

1. Vollstaendigen Feld-/Privatzustandscarry erneut validieren.
2. Konfigurationsdigest, Geometrie, Kanteninventar, Feldtick und Zeitendpunkt
   pruefen.
3. Rezeptordistribution und `MCMFieldStepTime` vor jeder Vorschlagsbildung
   gegeneinander pruefen.
4. Aus dem abgeschlossenen Feldvorzustand die drei Primaerfluesse bilden.
5. Den reinen S1-UG-Kern einmal auswerten.
6. Den ACM-Generator mit der unveraenderten neutralen Rezeptorgrenze
   kombinieren.
7. Aktivierung und schnellen Nachhall mit dem vorhandenen spektralen S/H-
   Integrator exakt vorschlagen.
8. Den Feldfolgezustand und beide bereits aus demselben Vorzustand
   vorgeschlagenen `z_next`-Werte vollstaendig binden.
9. Genau einen neuen Carry publizieren oder ohne Folgecarry abbrechen.

Der Feldgenerator liest nur `z_pre`. Kein `z_next` gelangt in den
Feldreadout desselben Intervalls. Feldfolgezustand und beide privaten
Folgezustaende bleiben Geschwister desselben Transaktionsvorzustands.

## Feldintegration

Der reine ACM-1H-Kern liefert einen symmetrischen Vier-mal-vier-Generator
aus den drei komponierten Kantenraten. Die Integration ersetzt damit nur
den neutralen internen Drei-Kanten-Generator. Unveraendert bleiben:

- die Rezeptordistribution;
- die lokale Rezeptorgrenze und ihre Primaerrate;
- `MCMFieldStepTime` und seine Dauer;
- der vorhandene exakte S/H-Integrator;
- die atomare `SharedMCMField.advance`-Materialisierung.

Es gibt keinen zusaetzlichen Feldquellterm, keine Normalisierung, kein
Clipping ausserhalb der bereits vorhandenen S/H-Domaenenpruefung und keinen
zweiten Primaerfluss auf der geteilten Kante.

## ACM-OFF

`advance_acm1h_off_four_node_field` nimmt ausschliesslich ein normales
Vier-Knoten-Feld und die vorhandenen neutralen Feldargumente entgegen. Der
Pfad ruft direkt `advance_neutral_fast_shared_field` auf.

Er erzeugt insbesondere nicht:

- `ACM1HPrivateState`;
- `ACM1HFieldCarry`;
- einen ACM-Entscheidungsrecord;
- einen ACM-Digest im Feldzustand.

Der synthetische Regressionstest bestaetigt fuer identische Eingaben
wert- und digestidentische Ausgabe zum direkten neutralen Feldpfad. Der
reine ACM-Referenzkern wird in diesem Test nachweislich nicht aufgerufen.

## Synthetische Abnahme

Die neue Testsuite prueft:

- unveraenderte Feldbindung bei der privaten Carrykonstruktion;
- einen aktiven atomaren Feld-/Zustandsschritt;
- die gemeinsame Fortschreibung beider `z`-Werte;
- einen gueltigen Carry-Folgeschritt;
- bitgenauen ACM-OFF-Bypass;
- Konfigurations- und Zeitfehlersperren;
- Verteilungs-/Intervallpruefung vor dem ACM-Vorschlag;
- atomaren Abbruch bei einem synthetischen Kernfehler;
- Unveraenderlichkeit, private API-Grenze und unveraenderten Snapshot.

Die fokussierte und direkt relevante Abnahme wird mit dem vorhandenen
`unittest`-Laufwerkzeug ausgefuehrt. `pytest` ist in der aktiven
Python-Umgebung nicht installiert und wurde nicht als neue Abhaengigkeit
hinzugefuegt.

Die Tests erzeugen ausschliesslich kontrollierte In-Memory-Vertragsschritte.
Sie sind kein formaler oder realer Forschungsfeldlauf und treffen keine
Ergebnisentscheidung ueber die Funktion des Kandidaten.

## Fail-closed-Verhalten

Ohne Folgecarry wird abgebrochen, wenn unter anderem:

- Feld- und Privatdigest nicht zusammenpassen;
- Konfiguration, Geometrie oder Kanteninventar abweichen;
- Feldtick oder Zeitendpunkt nicht anschliessen;
- Distribution und Schrittintervall nicht identisch gebunden sind;
- der reine Referenzkern keinen vollstaendigen Erfolgsrecord liefert;
- der komponierte Generator nicht symmetrisch und vierdimensional ist;
- der vorhandene S/H-Integrator seine Domaene verlaesst;
- nur ein Feld- oder nur ein Privatfolgezustand erzeugt werden koennte.

Es gibt keinen Reparaturpfad, keinen Fallback auf ACM-OFF und keinen
Teilcommit.

## Technische Entscheidung

```text
S1_UI_PRIVATE_ACM1H_FIELD_CARRY_IMPLEMENTED
ONE_ATOMIC_FOUR_NODE_FIELD_AND_Z_SIBLING_STEP_IMPLEMENTED
ACM_OFF_BIT_EXACT_DIRECT_NEUTRAL_BYPASS_CONFIRMED
PUBLIC_API_UNCHANGED
SHARED_FIELD_SNAPSHOT_UNCHANGED
NO_FORMAL_OR_REAL_FIELD_RUN
NO_ASSESSMENT_OF_MCM_MEMORY_DEVELOPMENT_SUITABILITY
```

S1-UI belegt damit ausschliesslich, dass der in S1-UH gebundene private
Integrationsvertrag technisch ausfuehrbar und synthetisch kontrollierbar
ist. Die bereits akzeptierte Reduzierbarkeit gegen allgemeinere gekoppelte
Gainmodelle bleibt bestehen. Die technische Eignung als moeglicher Baustein
der hypothetischen MCM-Memory-Entwicklungsrichtung ist damit noch nicht
bewertet.

## Naechster Forschungsabschnitt

Als naechster normaler Schritt ist S1-UJ zulaessig: ein rein statischer
Integrations-, Gegenbaseline- und Falsifikationsaudit. Er soll vor jeder
weiteren Ausfuehrung festlegen, welche kleinste synthetische G/O-
Integrationsmatrix ACM-1H gegen ACM-OFF, den vorhandenen E1-Kantengain und
eine faire gekoppelte Gainbaseline pruefen koennte.

S1-UJ darf keine neue Gleichung, keinen Parameter, keinen Code, keinen Test
und keinen Feldlauf erzeugen. Eine spaetere Ausfuehrung der Matrix benoetigt
danach eine eigene konkrete Freigabe.
