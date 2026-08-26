# S1-XF: Privater Miniaturrunner und Receiptabnahme

## Auftrag und Grenze

S1-XF implementiert den privaten Runner und seine unveraenderlichen
Bildungs-, Zell- und Gesamt-Receipts. Ausgefuehrt wird ausschliesslich eine
kleine synthetische Ersatzmatrix. Die registrierte S1-XA-Matrix mit 60
Zellen bleibt gesperrt.

Oeffentliche API, Snapshot, Dateien, Produktion, Feldwirkung und Semantik
werden nicht beruehrt. Der Runner erzeugt keine technische Funktions- oder
Baselineentscheidung und keinen Memory-Claim.

## Bildung vor Vorlagenvergleich

Der Runner materialisiert zuerst die private S1-XC-Fixture. Danach erzeugt
er fuer Audio und Video je einen leeren PPB-1-Zustand und fuehrt die drei
gebundenen Bildungsframes aus:

```text
0-1 -> CREATED
1-2 -> MATCHED
2-3 -> MATCHED
```

Erst nach diesen sechs `advance_ppb1_bank`-Aufrufen wird der gebildete
Zustand gegen die S1-XC-Vorlage verglichen. Bankdigest, Identitaetsdigest,
Zaehlwerte, Slotzustand, Stuetzung und Prototyp muessen uebereinstimmen.
Jede Abweichung stoppt vor der ersten Probe.

Bildungsreceipts:

```text
Audio: a0f04554313be9f3c7ef21e69673920f3d0ca392f498971e411e921e37ec2128
Video: ae59b7683383d73fb4949333a6c6c43b9499ea7f30ade7466bf0c7bd86f0f9fb
```

## Synthetische Ersatzmatrix

Die Miniaturmatrix verwendet eigene IDs mit dem Praefix `s1xf-mini` und nur
zwei vorgebundene Probearten:

```text
exact-positive
distinct-negative
```

Damit entstehen pro Lauf:

| Rolle | Anzahl |
|---|---:|
| Modalitaeten | 2 |
| Systeme | 6 |
| Probearten | 2 |
| Kandidatenzellen | 4 |
| Baselinezellen | 20 |
| Miniaturzellen gesamt | 24 |
| registrierte S1-XA-Zellen | 0 |

No-Memory behaelt seine Nullrollen. Replay meldet drei gespeicherte
Modalitaetsdimensionen und Historienzugriff. Kandidat und die drei einfachen
Einvektorbaselines melden je eine Dimension. Alle Probevorzustaende bleiben
unveraendert.

## Technischer Befund

Alle 2 Bildungs- und 24 Zellreceipts wurden einzeln validiert und atomar an
ein Gesamt-Receipt gebunden:

```text
Entscheidung:          MINIATURE_RUNNER_AND_RECEIPTS_VALID
Matrixreceipt-Digest: f89ff3d3afc9113b830054470622195670eff525583068e73da0026f615ce210
Modulquellhash:        8be32d731ea0a9220c4e5d020f4eb411b45c1caeecf958f7f4efcab43fea2319
```

`12 von 12` synthetische S1-XF-Abnahmetests bestehen. Dies bestaetigt nur
Runnerreihenfolge, Vorlagenvergleich, Receiptanatomie, Atomaritaet und
private Trennung. Es ist kein Ergebnis der registrierten technischen
Memory-Funktionspruefung und kein Nachweis einer MCM-spezifischen Memory.

## Naechster Schritt

S1-XG ist als rein statischer Quell-, Aufrufreihenfolge-, Receipt- und
Nichtausfuehrungsaudit vorgesehen. Er darf den Runner nicht erneut
ausfuehren. Die 60-Zellen-Matrix und Ergebnisentscheidung bleiben gesperrt.

## Grundlagen

- [S1-XE Runnervertrag](S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_ENTSCHEIDUNGSVERTRAG.md)
