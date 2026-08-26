# S1-UH: ACM-1H statischer Zustandspaar-, Atomaritaets-, Integrationsgrenz- und E1-Reduktionsaudit

## Auftrag und Grenze

S1-UH prueft nach der isolierten S1-UG-Implementierung, ob ACM-1H spaeter
ohne Aenderung des produktiven Feldsnapshots als privates Zustandspaar mit
dem vorhandenen MCM-Feld fortgeschrieben werden koennte. Der Audit bindet
Containerrollen, Vorzustandsordnung, atomaren Commit, ACM-OFF und die
Abgrenzung zum vorhandenen E1-Kantengain.

S1-UH implementiert keine Runtime, legt keinen neuen Test an und fuehrt
keinen Test oder Feldlauf aus. Der private Referenzkern aus S1-UG bleibt
unveraendert.

## Gepruefte vorhandene Muster

Der Codebestand besitzt bereits zwei relevante, aber fachlich getrennte
Muster:

1. `E1CoupledFastFieldStepResult` gibt ein vollstaendiges neues
   `SharedMCMField`, einen privaten E1-Endzustand und den angewandten Adapter
   gemeinsam zurueck.
2. `FourNodeModelCarry` traegt ein Feld und einen modellprivaten Zustand als
   digestgebundenes Paar ausserhalb des produktiven Feldsnapshots.

Damit ist ein privater Feld-/Modellzustandscarry strukturell bereits
darstellbar. Keines dieser Muster wird in S1-UH veraendert oder direkt als
ACM-1H-Runtime wiederverwendet.

## Kleinster privater ACM-1H-Zustand

Der spaetere fortbestehende ACM-1H-Zustand benoetigt fuer die offene
Vier-Knoten-Linie genau:

```text
schema_id
configuration_digest
geometry_id
edge_inventory_digest
field_tick
field_time_endpoint
z_left in [-1,1]
z_right in [-1,1]
state_digest
```

Nicht Bestandteil dieses Zustands sind:

- Knotenaktivierungen oder Nachhallwerte;
- Primaerfluesse, Faktoren oder Generatoren;
- Rezeptorwerte oder Eingangsrohdaten;
- `theta`, Paritaet oder Beteiligung des letzten Intervalls;
- Sequenz, Phase, Zielwert, Label oder Comparatorentscheidung;
- ein eigener Zeitstempel je Motiv.

Primaerfluesse, Motivvorschlaege und Komposition bleiben ephemere
Intervallrecords. Die zwei `z`-Werte sind die einzigen neuen fortbestehenden
Skalare.

## Kleinster privater Feld-/ACM-Paarcontainer

Ein spaeterer In-Memory-Carry darf genau folgende Rollen tragen:

```text
ACM1HFieldCarry
    field: SharedMCMField
    private_state: ACM1HPrivateState
    field_digest
    private_state_digest
    configuration_digest
    geometry_digest
    edge_inventory_digest
    carry_digest
```

Der Carry ist kein `SharedMCMFieldSnapshot` und wird nicht in dessen Payload
eingebettet. Feld und privater Zustand muessen dieselbe Geometrie, dasselbe
Kanteninventar, denselben abgeschlossenen Feldtick und denselben
Feldzeitendpunkt bezeichnen.

Eine erneute Laufaufnahme nach Prozessende ist in diesem Korridor nicht
zugelassen. Dafuer waere spaeter ein eigener privater Paarsnapshotvertrag
noetig. Der bestehende Feldsnapshot allein darf nicht als vollstaendige
ACM-1H-Wiederaufnahme ausgegeben werden, weil ihm die zwei `z`-Werte fehlen.

## Unveraenderlicher Transaktionsvorzustand

Eine spaetere gekoppelte Transaktion liest genau ein Paar `TX_PRE`:

```text
TX_PRE = (field_pre, acm_state_pre)
```

Vor jeder Vorschlagsbildung muessen gemeinsam validiert werden:

- Feld-, Geometrie- und Kanteninventaridentitaet;
- Konfigurationsdigest;
- Feldtick und Feldzeitendpunkt;
- beide endlichen `z`-Werte;
- explizites naechstes `MCMFieldStepTime`;
- zugehoerige Rezeptordistribution und ihre identische Zeitgrenze;
- vollstaendige offene Vier-Knoten-Geometrie.

Nach Beginn der Vorschlagsbildung ist `TX_PRE` unveraenderlich. Kein
Motivvorschlag liest einen bereits erzeugten Motivfaktor, einen neuen
Feldwert oder `z_next`.

## Geschwistervorschlag und Integrationsordnung

Die einzig zulaessige kausale Ordnung lautet:

1. `TX_PRE`, Konfiguration, Distribution und Feldintervall validieren.
2. Primaere Kantenraten und signed Fluesse aus `field_pre` ableiten.
3. Den reinen S1-UG-Kern genau einmal aus `TX_PRE` auswerten.
4. Aus dessen Faktoren die drei nichtnegativen komponierten Kantenraten
   bilden.
5. Aus denselben abgeschlossenen Eingaben den primaeren Rezeptorrand bilden.
6. S/H mit dem konstanten komponierten Generator ueber das Intervall exakt
   vorschlagen.
7. Das vollstaendige neue `SharedMCMField` ohne Teilcommit materialisieren.
8. Feldfolgezustand und beide bereits vorgeschlagenen `z_next` gemeinsam
   gegen Geometrie, Zeit, Endlichkeit und Digests validieren.
9. Genau ein neues `ACM1HFieldCarry` zurueckgeben oder ohne Ausgabe
   abbrechen.

Der Feldreadout verwendet ausschliesslich `z_pre`. `z_next` wird nicht fuer
den Generator desselben Intervalls gelesen. Feld- und Zustandsfolgezustand
sind damit Geschwister desselben Vorzustands und keine Write-then-read-Kette.

## Warum die E1-Halbschrittfolge nicht uebernommen wird

Die vorhandene E1-Runtime verwendet:

```text
halber E1-Schritt -> S/H-Feldschritt -> halber E1-Schritt
```

Der mittlere E1-Zustand bestimmt dabei den angewandten Kantengain. Diese
Strang-artige Ordnung ist fuer E1s eigene kontinuierliche Bindungs- und
Freigabedynamik gebunden.

ACM-1H hat dagegen in S1-UE festgelegt:

```text
z_pre -> Feldreadout
z_pre + aktuelle Primaerfluesse -> z_next
```

Eine ACM-Halbschrittfolge wuerde einen bereits fortgeschriebenen Zustand in
den Feldreadout desselben Intervalls einfuehren und damit den gebundenen
Geschwistervertrag verletzen. E1s Kopplungsfunktion darf deshalb nicht durch
blosse Parameter- oder Typersetzung fuer ACM-1H verwendet werden.

Wiederverwendbar sind nur allgemeine technische Primitive wie kanonisches
Kanteninventar, symmetrische Generatorbildung, exakte S/H-Integration und
immutable Ergebniscontainer.

## Exakter ACM-OFF-Bypass

`ACM-OFF` ist kein aktiver ACM-1H-Zustand mit neutralem Zahlenwert. Der
Bypass muss vor jeder ACM-1H-Zustands- oder Vorschlagsbildung entscheiden:

```text
ACM-OFF
-> direkter vorhandener neutraler Feldpfad
-> kein ACM1HPrivateState
-> kein ACM1HFieldCarry
-> kein ACM-Digest oder neutraler Container
```

Der ausgegebene Feldzustand muss fuer dieselben Eingaben wert- und
digestidentisch zum unveraenderten neutralen Feldkern sein.

Davon getrennt bleibt `z = 0` im aktiven ACM-Pfad. Dort ist der aktuelle
Readout neutral, aber eine echte Zwei-Kanten-Beteiligung darf `z_next`
bilden. `ACM-OFF` und `z = 0` duerfen deshalb weder denselben Carry noch
denselben Zustandsclaim besitzen.

## Abgrenzung gegen den vorhandenen E1-Gainadapter

### E1

Der vorhandene E1-Korridor besitzt auf der Vier-Knoten-Linie drei
nichtnegative Einzelkantenbindungen. Seine Schreibung:

- liest je Kante den quadrierten Aktivierungsunterschied;
- ist damit gegen das Kantenflussvorzeichen invariant;
- bindet und gibt eine endliche lokale Ressource frei;
- besitzt autonomes Release;
- skaliert jede Kante aus ihrem eigenen Binding;
- verstaerkt die Basisrate, kehrt sie aber nicht motivgemeinsam um.

### ACM-1H

ACM-1H besitzt zwei signed Motivzustaende. Seine Schreibung und Wirkung:

- liest die gemeinsame Paritaet zweier benachbarter Kanten;
- unterscheidet gleich- und gegengerichtete Zwei-Kanten-Lagen;
- haelt ohne gemeinsame Beteiligung statt autonom abzuklingen;
- skaliert beide Kanten eines Motivs mit demselben Faktor;
- kann vorhandenen passiven Transport verstaerken oder abschwaechen;
- komponiert zwei Motivfaktoren auf der gemeinsamen Kante.

## Verbleibende Gegenprognose zu E1

Die in S1-UE gebundene G/O-Paarung besitzt auf jeder einzelnen Kante
dieselbe absolute Exposition. Der vorhandene E1-Schreiber verwendet genau
diese quadrierte Einzelkantenaktivitaet und muss deshalb bei identischem
E1-Vorzustand dieselben drei Bindings fortschreiben.

ACM-1H sagt fuer dieselben Geschichten entgegengesetzte signed
Motivzustaende voraus. Unter derselben spaeteren positiven Probe darf es
deshalb verschiedene gemeinsame Faktoren liefern, waehrend E1 denselben
vollstaendigen Kantenzustand und dieselbe Fortsetzung traegt.

Diese Gegenprognose ist gegen den konkret vorhandenen E1-Adapter technisch
eigenstaendig und rechtfertigt einen spaeteren isolierten
Integrationsvergleich. Sie ist keine Nichtreduzierbarkeit gegen beliebige
Adapter.

## Breitere Reduktionsgrenze

Ein allgemeiner gekoppelter Zwei-Kanten-Gain mit zwei signed
Motivkoordinaten, Paritaetsleser und identischem Feldreadout kann ACM-1H
vollstaendig reproduzieren. Ebenso kann eine hinreichend allgemeine lokale
Zustandsmaschine die endliche Transaktion darstellen.

Die Runtimeintegration wuerde daher keine neue Mechanik belegen. Ihr
moeglicher Engineeringwert ist enger:

- explizite gemeinsame Motivempfaenglichkeit;
- kontrollierte Gegenwirkung statt autonomem Leak;
- transparentes G/O-Verhalten gegen vorhandene kantenweise Baselines;
- kompatible passive Einbettung in den technischen MCM-Feldkern.

## Fail-closed-Integrationsgrenzen

Eine spaetere Transaktion muss ohne Carryausgabe abbrechen, wenn:

- Feld und privater Zustand unterschiedliche Zeit- oder Geometrierollen
  tragen;
- das Kanteninventar oder ein Digest abweicht;
- der S1-UG-Kern keinen vollstaendigen Erfolgsrecord liefert;
- `z_next` in den Feldreadout desselben Intervalls gelangt;
- der Feldintegrator einen anderen Generator als den validierten
  ACM-Kompositionsrecord verwendet;
- nur Feld oder nur privater Zustand materialisiert wird;
- ACM-OFF einen privaten Zustand oder ACM-Digest erzeugt;
- ein neutraler `z`-Zustand faelschlich als ACM-OFF behandelt wird;
- Clipping, Reset, Nachnormalisierung oder Fallback einen Fehler repariert;
- Motiviterationsreihenfolge den finalen Carrydigest veraendert;
- ein normaler Feldsnapshot als vollstaendige ACM-Wiederaufnahme verwendet
  werden soll.

## Auditentscheidung

Ein privater atomarer Feld-/ACM-Zustandscarry ist ohne Aenderung des
produktiven Feldsnapshots statisch darstellbar. Der S1-UG-Kern liefert die
vollstaendigen Geschwistervorschlaege; vorhandene Feldprimitive koennten den
komponierten symmetrischen Generator exakt integrieren. ACM-OFF kann den
neutralen Feldpfad direkt und ohne privaten Rest verwenden.

Gegen den konkret vorhandenen E1-Adapter verbleibt eine klare technische
G/O-Gegenprognose. Gegen breitere gekoppelte Gainmodelle bleibt ACM-1H
reduzierbar. Damit ist eine spaetere isolierte Runtimepruefung methodisch
begruendbar, aber noch nicht freigegeben.

```text
S1_UH_PRIVATE_FIELD_ACM_STATE_PAIR_STATICALLY_ADMISSIBLE
PRESTATE_SIBLING_PROPOSAL_AND_ATOMIC_PAIR_COMMIT_BOUND
ACM_OFF_DIRECT_NEUTRAL_BYPASS_WITHOUT_PRIVATE_CARRY_BOUND
CURRENT_E1_EDGE_GAIN_DOES_NOT_REPRODUCE_MATCHED_G_O_PARITY_RESPONSE
BROADER_COUPLED_GAIN_REDUCTION_REMAINS_ACCEPTED
NO_RUNTIME_IMPLEMENTATION_NO_TEST_NO_FIELD_RUN
```

## Erforderliche naechste Freigabe

Die statische Integrationsarchitektur ist bis zur Implementierungsgrenze
geschlossen. Der naechste moegliche Abschnitt waere S1-UI:

```text
privater In-Memory-ACM1HFieldCarry
+ genau ein atomarer Vier-Knoten-Schritt
+ synthetische Integrations- und ACM-OFF-Regressionstests
+ keine oeffentliche API
+ kein Snapshotumbau
+ kein Feldlauf
```

Dieser Schritt wuerde erstmals Runtimeintegrationscode erzeugen und ist von
der bisherigen Freigabe ausdruecklich ausgeschlossen. Ein allgemeines
`ok weiter` hebt diese Sperre nicht auf. S1-UI benoetigt eine neue konkrete
Freigabe, die den privaten In-Memory-Schritt und synthetische Tests erlaubt,
aber oeffentliche API, Snapshotumbau und Feldlaeufe weiterhin sperrt.
