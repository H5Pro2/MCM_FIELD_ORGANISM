# S1-JO: Privater reiner gemeinsamer Intervallmaterializer

## Ergebnis

S1-JO implementiert den in S1-JN gebundenen privaten Materializer. Er bereitet
genau ein registriertes gemeinsames Intervall fuer genau eine Modellrolle vor
und erzeugt getrennte Integritaetsrecords. Er ruft weder DTS-1 noch eine der
Baselines B1 bis B6 auf.

## Implementierter Umfang

Das private Modul enthaelt:

- 23 unveraenderliche, wertgepruefte S1-JK-Envelopefixtures,
- rollengebundene private Vorzustandsobjekte fuer DTS-1 und B1 bis B6,
- eine Modellaufrufhuelle aus Feld, Distribution, Zeit und Geometriedigest,
- einen getrennten Integritaetsrecord mit vier Digestrollen,
- einen reinen Materializer mit den sechs in S1-JN gebundenen Argumenten,
- einen statischen technischen Abnahmereceipt.

Der Materializer prueft Feld-, Layer-, Geometrie-, Neuronen-, Rezeptor-, Dock-
und Mappingidentitaeten fail-closed. Frische Sequenzanfange sowie getragene
Vorgaenger-, Output- und Zeitprovenienz werden vor jeder Ausgabe validiert.

## Reine Vorzustandsoperationen

`INITIAL_REGISTERED_SH` ersetzt nur den registrierten S/H-Anfangszustand.
`CARRY_PRIOR_SH` gibt dasselbe Feldobjekt weiter. `APPLY_BOUNDARY_2N` und
`APPLY_BOUNDARY_3N` delegieren an die bereits geprueften privaten reinen
Grenzoperatoren. Keine dieser Operationen verbraucht Feldzeit oder vollzieht
einen Felduebergang.

## Digestgrenzen

Die vier Rollen bleiben getrennt:

- Common Exposure bindet Geometrie, S/H-Operation, Distribution und Zeit.
- Private Prestate bindet Modellrolle, vollstaendiges Eingabefeld, privaten
  Zustand und Vorgaengerprovenienz.
- Materialized Input bindet ausschliesslich die vier vorbereiteten
  Modellaufrufwerte.
- Orchestration Control bindet Sequenz, Ordinal, Intervall, Checkpoint und
  gegebenenfalls den Kandidatensidecar.

Payloads werden wertbasiert als kompaktes UTF-8-JSON kanonisiert, negatives
Null wird auf positives Null abgebildet und SHA-256 wird als Digestverfahren
verwendet. Kontrolllabels und private Zustaende gelangen nicht in die
Modellaufrufhuelle. Der modelluebergreifende Vergleich gleicher Common-
Exposure-Digests bleibt Aufgabe einer spaeteren Orchestrierung.

## Technische Abnahme

Vierzehn fokussierte Tests decken die zwanzig in S1-JN gebundenen Klassen ab:
Fixturevollstaendigkeit, alle sieben Rollen, die vier Vorzustandsoperationen,
Identitaet, Carry- und Zeitprovenienz, unveraenderte Eingaben, Digesttrennung,
Determinismus, Kanonisierung und atomare Fehlerausgabe.

Es wurden null Modellkerne, null Baselineadapter, null technische
Felduebergaenge und null Forschungsschritte ausgefuehrt.

## Entscheidung

`PRIVATE_PURE_COMMON_INTERVAL_MATERIALIZER_IMPLEMENTED_TECHNICALLY_ACCEPTED`

Kanonischer Receiptdigest:

`6c4bd17ae11f9e6cc1e71f7d88a089df982b0acefc1a9800f7f80b3386de0806`

S1-JO belegt ausschliesslich die technische Materialisierbarkeit des
registrierten Intervallinputs. Baselinepassung, numerische Zulaessigkeit,
Profilvergleich und eine eigene DTS-1-Gegenprognose sind nicht gezeigt.
Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JP darf ausschliesslich vor jeder Baselineimplementierung den privaten
Adapterumfang fuer B1 bis B6 gegen die vierwertige Modellaufrufhuelle und die
rolleneigenen bestehenden Kern-APIs statisch pruefen. Informationszugriff,
Ein-/Ausgabe, Zustandsrueckgabe, Fehleratomaritaet und neutrale Ablation sind
vor Code zu binden. Noch kein Adaptercode, Modellaufruf, Profilvergleich,
keine Runtime oder Forschungsprobe.
