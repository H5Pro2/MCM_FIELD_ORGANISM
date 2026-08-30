# S2-HD: Statischer Artefaktgroessen- und Projektionsaudit

Status: `S2HD_STATIC_AUDIT_COMPLETE_COMPACT_PROJECTION_CONTRACT_REQUIRED`

## Grenze

S2-HD ist ausschliesslich ein statischer Audit. Es wurden keine Projektmodule
importiert, keine Speicher-, Rezeptor-, Projektions- oder Auswertungsfunktion
aufgerufen und kein Test oder Funktionslauf ausgefuehrt. Der bestehende Lauf
`s2hc-context-function-20260830-01` bleibt dauerhaft `NOT_EVALUABLE`.

Unveraendert bleiben insbesondere:

- der vollstaendige In-Memory-Nachzustand;
- B4, TSPM-1 und PPB-1;
- S2-GJ-Verbraucher, Baseline und Auswertungsregeln;
- die Operationsregistry mit 139 Operationen und 278 Ereignissen;
- die Einzel- und Gesamtbudgets;
- die Fehlercodeweitergabe, insbesondere `E008`.

## Beleggrundlage

Der erste Composite-Schritt aus S2-HC konnte nicht als Receipt veroeffentlicht
werden. Fuer seine statische Rematerialisierung wurde ein bereits vollstaendig
aufgezeichneter `B4TSPM1StepResult` aus S2-FZ verwendet. S2-FZ und S2-HC binden
dieselbe Koordinatorquelle:

```text
95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0
```

Die konkrete erste S2-GT-Quelle, die kuerzeren S2-GT-Ownerkennungen und die
aktuelle Recorderhuelle wurden statisch eingesetzt. Digests wurden nur als
gleich lange, bereits gebundene Identitaeten behandelt. Es wurde kein
Nachzustand neu berechnet.

Der Recorder akzeptiert eine Artefaktdatei bis zur Registrygrenze. Der
Verifikator verlangt jedoch `Dateigroesse < output_max_bytes`. Fuer eine
4.096-Byte-Rolle betraegt die effektiv verifizierbare Obergrenze daher 4.095
Byte.

## Composite-Receipt

Das kanonische S2-HC-Artefakt fuer `op-0003` benoetigt statisch **7.821 Byte**.
Die Registry erlaubt 4.096 Byte. Der ausgelieferte Fehler `E008` ist daher
korrekt.

Die wesentlichen erneut serialisierten Bestandteile des ersten Resultats sind:

| Bestandteil | kanonische Einzelgroesse |
| --- | ---: |
| `poststate` | 4.997 Byte |
| `receipt` | 1.081 Byte |
| `owner_poststate` | 728 Byte |
| `resource_ledger` | 519 Byte |
| `result_digest` | 66 Byte |
| `schema` | 38 Byte |

Die Einzelgroessen enthalten jeweils ihren eigenen JSON-Abschluss und sind
deshalb nicht direkt zur Huelle zu addieren. Sie zeigen aber eindeutig die
Ursache: Der vollstaendige Composite-Nachzustand wird im Receipt erneut
dupliziert, obwohl seine Teilzustaende und Identitaeten bereits digestgebunden
sind.

Die statische Uebertragung aller 18 vorhandenen S2-FZ-Compositeformen auf die
kuerzeren binaeren S2-GT-Werte ergibt fuer die vollserialisierte Huelle einen
Bereich von etwa 7,8 bis 9,2 KiB. Bereits der kleinste erreichbare erste
Bildungsschritt aller vier Geschichten ueberschreitet die Grenze. Damit sind
nicht nur einzelne spaetere Belegformen betroffen, sondern die gesamte
52-Schritt-Formation mit der aktuellen Projektion.

## Nachfolgende Artefaktrollen

Alle Rollen wurden gegen ihre eigene Registrygrenze und zusaetzlich gegen die
4.096-Byte-Ereignisgrenze geprueft. START- und RESULT-Ereignisse enthalten nicht
das volle Artefakt, sondern nur kleine Quellen- beziehungsweise
Artefaktdigestbindungen und bleiben unter 4.096 Byte.

| Rolle | Anzahl | statische oder vorhandene Groesse | Grenze | Befund |
| --- | ---: | ---: | ---: | --- |
| Reservation und Plan | 1 | vorhandene S2-HC-Dateien innerhalb 20.480 | 20.480 | gueltig |
| kompaktes `ReceptorReceipt` | 57 | 2.747-2.765, S2-HB qualifiziert; S2-HC konkret 2.748 | 4.096 | gueltig |
| volles `FormationReceipt` | 52 | erstes konkret 7.821; statische Folgeprognose ca. 7,8-9,2 KiB | 4.096 | **Blocker** |
| `ContextReadOnlyReceipt` | 4 | ca. 7.060-7.070 | 16.384 | gueltig |
| `MaskedProbeReceipt` | 1 | ca. 696 | 4.096 | gueltig |
| volle `S2GCProjectionReceipt` | 4 | stabile Vollform ca. 4.005; Abwesenheitsform ca. 2.569 | 4.096 | formal gueltig, nur 90 Byte Reserve |
| volle `S2GIProjectionReceipt` | 4 | stabile Vollform ca. 4.545; Abwesenheitsform ca. 3.110 | 4.096 | **Blocker** |
| `ArmReceipt` | 7 | groesste gebundene Vervollstaendigungsform ca. 1.867 | 8.192 | gueltig |
| `ExecutionEvidencePackage` | 1 | ca. 10.721 | 131.072 | gueltig |
| `EvaluationRunBinding` | 1 | ca. 489 | 8.192 | gueltig |
| `EvaluationReceipt` | 4 | ca. 923 | 8.192 | gueltig |
| `FinalEvidencePackage` | 1 | ca. 13.480 | 65.536 | gueltig |
| `CompletionCandidate` | 1 | ca. 442 | 4.096 | gueltig |
| `CompletionMarker` | 1 | ca. 371 | 2.048 | gueltig |

Die S2-GC-Vollform ist fuer die konkret gebundenen Faelle statisch knapp
materialisierbar. Sie ist mit nur 90 Byte Abstand zur effektiven Grenze jedoch
keine belastbare Aufzeichnungsform. Eine geringfuegig laengere zulassige
Kennung oder Zahlendarstellung koennte denselben Fehler erneut ausloesen. Sie
muss deshalb vor einem weiteren Hauptlauf ebenfalls kompakt gebunden oder mit
einem exakten, verifikatorgleichen Maximalbeleg abgesichert werden.

Die volle S2-GI-Projektion ist bereits bei einer stabilen auditiven und
visuellen B-Komponente eindeutig zu gross. Ohne Korrektur wuerde ein neuer Lauf
nach einer Reparatur der Formation spaetestens an der Zwei-Bereich-Projektion
erneut mit `E008` stoppen.

## Erforderliche Projektionsgrenzen

Ein folgender, gesondert freizugebender Korrekturvertrag muss mindestens drei
Aufzeichnungsprojektionen binden. Er darf die zugehoerigen vollstaendigen
In-Memory-Objekte weder ersetzen noch veraendern.

### 1. `CompactCompositeFormationReceiptV1`

Erhalten bleiben muessen:

- Operation, Geschichte, Quellordinalzahl und direkter Receptor-Receipt-Elter;
- Konfigurations-, Eingabe-, Vorzustands- und Nachzustandsdigest;
- B4-Ereignis, Slot-ID und B4-Nachzustandsdigest;
- TSPM-Result-, TSPM-Receipt- und TSPM-Nachzustandsdigest;
- Step-Receipt- und Composite-Resultdigest;
- Generation, Parent-State-Digest und Last-Input-Digest;
- der vollstaendige numerische Ressourcenledger samt Ledgerdigest;
- der vollstaendige Owner-Nachzustandsbeleg samt Status und Einmalverbrauch.

Nicht erneut gespeichert werden duerfen der volle B4-Zustand, Fast-Slots,
PPB-1-Baenke und Prototypwerte. Diese bleiben im unveraenderten In-Memory-
`B4TSPM1StepResult` erhalten und werden im Receipt ausschliesslich ueber ihre
bereits vorhandenen Digests gebunden.

Eine statische Referenzprojektion dieser Form liegt inklusive Recorderhuelle
bei rund 2,9 KiB und damit unter der unveraenderten 4.096-Byte-Grenze.

### 2. kompakte S2-GC-Projektionsaufzeichnung

Der vollstaendige `PerceptualContextBundle` bleibt In-Memory-Eingang fuer
S2-GI. Die Aufzeichnung benoetigt nur:

- Bundle-, Binding-, Konfigurations-, Quellen-, Probe- und Zustandsdigests;
- die drei Rollenzustaende und ihre Finding-/Kandidatendigests;
- Sequenzstatus und Sequence-Finding-Digest;
- vollstaendige endliche Ledgerzaehler und Ledgerdigest;
- identische Vor-/Nachzustandsdigests und `automatic_selection = null`.

Komponentenwerte duerfen nur durch ihre bereits im Bundle gebundenen Werte-
und Komponentendigests referenziert werden. Der Nachfolger S2-GI muss weiterhin
das vollstaendige In-Memory-Bundle erhalten; sein START-Beleg bindet den
semantischen Bundledigest und den kompakten Artefaktdigest getrennt.

### 3. kompakte S2-GI-Projektionsaufzeichnung

Der vollstaendige `TwoAreaContextBundle` bleibt In-Memory-Eingang fuer den
Verbraucher und die direkte Baseline. Die Aufzeichnung erhaelt:

- Source-Bundle-, Binding-, Konfigurations-, Quellen-, Probe- und
  Zustandsdigests;
- genau die zwei Bereichsrollen und ihre Findingdigests;
- Status und Kandidatendigest je oeffentlichem Bereich;
- den vollstaendigen endlichen Ressourcenledger;
- Vor-/Nachzustandsdigest, `automatic_selection = null` und Bundledigest.

Vollstaendige Komponenten und Werte werden nicht dupliziert. Die nachfolgenden
Arme binden sowohl den semantischen `TwoAreaContextBundle.bundle_digest` als
auch den Digest der kompakten Aufzeichnung, verwenden funktional aber weiterhin
das unveraenderte In-Memory-Bundle.

## Relationale und Fehlergrenzen

Fuer alle kompakten Formen gilt:

- der Recorderartefaktdigest und der semantische Ergebnisdigest bleiben
  verschiedene, explizit gebundene Rollen;
- jeder Nachfolger bindet den unmittelbar zugehoerigen Receipt- oder
  Bundledigest und den vorherigen Ereignisdigest;
- kein Digest darf von einem spaeteren Ergebnis oder einer Sollauswertung
  abgeleitet werden;
- der Verifikator prueft Schema, exakte Feldmenge, kanonische Kodierung,
  Registryrolle, Owner, Reservierung, START-Elter und Nachfolgerbindung;
- jede Groessenueberschreitung bleibt `E008`;
- die in S2-GY/S2-GZ gebundene Fehlercodeentscheidung bleibt unveraendert;
- Gesamtbudgets werden nicht erhoeht. Kompaktere Dateien verbrauchen lediglich
  weniger vom bestehenden Budget.

## Entscheidung

S2-HD ist bestanden als statischer Ursachen- und Folgeaudit. Der Befund ist
kein negativer Kontext- oder Memory-Befund. Er zeigt zwei sichere
Aufzeichnungsblocker und einen zu knappen Grenzfall:

1. volles Composite-Formationsergebnis;
2. volle S2-GI-Zwei-Bereich-Projektion;
3. volle S2-GC-Projektion mit unzureichender Sicherheitsreserve.

Vor einem weiteren Hauptlauf ist ein enger statischer Korrekturvertrag fuer
diese drei kompakten Aufzeichnungsprojektionen erforderlich. Erst danach sind
Implementierung, neutrale Qualifikation und ein neuer Funktionslauf getrennt zu
entscheiden.
