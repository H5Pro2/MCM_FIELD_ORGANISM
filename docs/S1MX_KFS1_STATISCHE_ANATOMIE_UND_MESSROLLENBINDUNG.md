# S1-MX KFS-1 statische Anatomie- und Messrollenbindung

## Status

S1-MX ist eine reine Anatomie- und Messrollenbindung fuer `KFS-1`.
Der Schritt bindet keine Gleichung, keine Parameter, keine Runtime, keinen
Feldlauf, keine Matrixpublikation und kein Urteil.

`KFS-1` bleibt ein Kandidatenraum:

```text
lokales ressourcenbegrenztes Feld-Substrat
mit Kohaerenzbelastung und spaeterer Aufnahmeaenderung
```

Diese Datei beweist keine Funktion. Sie legt nur fest, welche lokalen
Rollen, Bilanzen und Messflaechen spaeter vorhanden sein muessen, damit eine
Kandidatendynamik ueberhaupt pruefbar waere.

## Zweck

S1-MX verhindert, dass `KFS-1` vorzeitig als Gleichung, Runtime oder
Faehigkeit behandelt wird. Vor jeder Dynamik muss die statische Anatomie
eindeutig sein:

- welche lokale Ressource existiert;
- wo sie bilanziert wird;
- welche Feldwerte nur gelesen werden;
- welche Messrollen spaeter vergleichen duerfen;
- welche Zustaende fail-closed ungueltig sind.

## Lokale Anatomie

`KFS-1` darf nur aus lokalen, vorregistrierten Einheiten bestehen.

| Rolle | Bindung |
|---|---|
| `carrier_id` | lokaler Feldtraeger innerhalb der MCM-Geometrie; keine Semantik, kein Label |
| `edge_id` | eindeutige lokale Kante zwischen zwei gebundenen Traegern |
| `field_sample` | read-only S/H-Feldzustand an der lokalen Kante oder ihren Endpunkten |
| `resource_account` | endliches Ressourcenkonto der lokalen Kante |
| `measurement_slot` | vorab benannte Messstelle fuer Spaetaufnahme, Abschwaechung, Interferenz, Freigabe oder Wiederbindung |

Die Kantenidentitaet wird durch die beteiligten Traeger und die registrierte
lokale Geometrie bestimmt. Eine Kante darf waehrend eines spaeteren Vergleichs
nicht stillschweigend umbenannt, neu sortiert oder durch eine andere lokale
Nachbarschaft ersetzt werden.

## Ressourcenrollen

Jede zulaessige `KFS-1`-Kante besitzt genau ein endliches Ressourcenkonto mit
drei disjunkten Rollen:

| Rolle | Bedeutung |
|---|---|
| `free` | lokal verfuegbare Ressource ohne aktuelle Bindung |
| `bound` | lokal durch eine registrierte Feldgeschichte gebundene Ressource |
| `blocked` | lokal nicht verfuegbare refraktaere Ressource |

Weitere Rollen sind in S1-MX nicht zugelassen. Insbesondere gibt es keine
versteckte Reserve, keinen globalen Ausgleichstopf und keinen Puffer fuer
Rohdaten oder Sequenzen.

## Lokale Erhaltungsidentitaet

Fuer jede registrierte Kante gilt statisch:

```text
capacity(edge_id) = free(edge_id) + bound(edge_id) + blocked(edge_id)
```

Die Identitaet ist nur eine Bilanzbedingung. Sie ist keine Dynamikgleichung.

Gueltig ist ein spaeterer Datensatz nur, wenn:

- `capacity(edge_id)` endlich und vorab registriert ist;
- `free`, `bound` und `blocked` nicht negativ sind;
- die Summe exakt der registrierten Kapazitaet entspricht;
- alle Rollen derselben `edge_id` zugeordnet bleiben;
- keine andere Struktur dieselbe Ressource doppelt zaehlt.

## Messrollen

S1-MX bindet nur, welche Messrollen spaeter existieren muessen.

| Messrolle | Darf messen | Darf nicht tun |
|---|---|---|
| `disturbance_read` | lokale S/H-Spannung vor einer moeglichen Ressourcenbindung | Feldzustand schreiben oder Sequenzen speichern |
| `late_reception_read` | spaetere Aufnahme derselben lokalen Probe unter gleicher Geometrie | Differenz durch Klassifikation erzeugen |
| `attenuation_observer` | Veraenderung einer gebundenen Wirkung nach Loesungs- oder Folgegeschichte | Abschwaechung nachtraeglich auswaehlen |
| `interference_observer` | gerichtete Differenz zwischen konkurrierender und nicht konkurrierender Vorgeschichte | globale Ueberschreibung als lokale Interferenz ausgeben |
| `release_observer` | Uebergang aus `bound` oder `blocked` in `free` | Kapazitaet erzeugen oder verschwinden lassen |
| `rebinding_observer` | neue lokale Beanspruchung zuvor freier Ressource | Replay oder Rohdatenrueckgriff verwenden |

Alle Messrollen sind passive Beobachter. Sie duerfen keine Kandidatenwirkung
erzeugen.

## Verbotene Zustaende

Ein `KFS-1`-Anatomierecord ist ungueltig, wenn mindestens eine Bedingung gilt:

- eine Ressourcenrolle ist negativ;
- `free + bound + blocked` unterscheidet sich von `capacity`;
- eine Kante besitzt keine eindeutige lokale Identitaet;
- eine Ressource wird auf mehreren Kanten doppelt bilanziert;
- ein Readout schreibt in das Feld oder in das Ressourcenkonto;
- Rohdaten, Labels, Reward, Zieltopologie oder Sequenzpuffer gelangen in den
  Feldzustand;
- eine Baseline sieht eine andere relevante A/B/Gap-Vorgeschichte;
- ein globaler Normalisierer ersetzt die lokale Ressourcenbilanz;
- ein Fixed Adapter, Leaky-Nachhall oder Integrator wird als KFS-1-Anatomie
  umbenannt.

Alle ungueltigen Zustaende muessen fail-closed behandelt werden.

## Abgrenzung zu Baselines

`KFS-1` ist strukturell nur dann ein eigener Kandidatenraum, wenn sein lokales
Ressourcenledger nicht auf folgende Strukturen reduziert wird:

| Struktur | Abgrenzung |
|---|---|
| Fixed Adapter | besitzt keine zustandsabhaengige lokale Ressourcenbilanz |
| Gain | skaliert Feldanteile, fuehrt aber kein `free/bound/blocked`-Ledger |
| schneller Nachhall | ist passive S/H-Persistenz ohne endliche Ressourcenfreigabe |
| Integrator | akkumuliert Zustand, ohne zwingende lokale Freigabe und Wiederbindung |
| Replay | gibt Folgegeschichte aus einem Puffer wieder |
| Readout-Klassifikator | erzeugt Unterschiede erst in der Auswertung |

Zustandsbehaftete Baselines muessen spaeter dieselbe relevante kausale
Vorgeschichte sehen. Wenn eine Baseline kein Ressourcenledger besitzt, wird
das als Null- oder Nichtzutreffend-Anatomie protokolliert, nicht als
nachtraeglich reparierte Ressource.

## Anatomietests

S1-MX erlaubt nur Tests fuer Anatomie, Bilanz und fail-closed-Verhalten:

- Kantenidentitaet ist eindeutig und reproduzierbar;
- jede Kante besitzt genau ein endliches Ressourcenkonto;
- `free`, `bound` und `blocked` sind disjunkt;
- die lokale Erhaltungsidentitaet ist pruefbar;
- ungueltige Summen, negative Rollen und doppelte Ressourcen scheitern;
- Messrollen bleiben passiv;
- Baselineprofile ohne aequivalente Vorgeschichte werden gesperrt.

Nicht erlaubt sind Tests auf Wirkung, Memory, Lernen, Systemfaehigkeit,
Feldintelligenz, biologische Gleichsetzung oder offene Weltuebertragung.

## Ergebnis von S1-MX

S1-MX bindet:

- lokale Kanten- und Traegerrollen;
- das `free/bound/blocked`-Ressourcenledger;
- die lokale Erhaltungsidentitaet;
- passive Messrollen;
- verbotene Zustaende;
- strukturelle Baselineabgrenzung;
- erlaubte Anatomie- und Fail-Closed-Tests.

S1-MX bindet nicht:

- Gleichung;
- Parameter;
- Zahlenwerte;
- Runtime;
- Feldlauf;
- Funktionsnachweis;
- hypothetische MCM-Memory;
- Ergebnisentscheidung.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-MY, ausschliesslich als statischer Schema- und
Digestvertrag fuer KFS-1-Anatomierecords und Messrollenrecords. S1-MY darf
nur festlegen, welche Felder, IDs, Digests und Fail-Closed-Pruefungen spaeter
maschinell reproduzierbar sein muessen. Gleichung, Parameter, Runtime,
Ausfuehrung und Funktionsentscheidung bleiben gesperrt.
