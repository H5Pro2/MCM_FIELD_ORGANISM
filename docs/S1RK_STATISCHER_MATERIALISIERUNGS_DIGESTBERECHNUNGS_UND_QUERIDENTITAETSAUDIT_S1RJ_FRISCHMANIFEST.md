# S1-RK: Statischer Materialisierungs-, Digestberechnungs- und Queridentitaetsaudit des S1-RJ-Frischmanifests

## Status und Umfang

S1-RK materialisiert die in S1-RJ gebundenen Vier-Knoten-Praeimages genau
einmal als statisches Manifest, berechnet ihre kanonischen SHA-256-Digests
und prueft die gemeinsamen Identitaeten quer ueber alle 14 Modellrollen.

Das Manifest liegt unter:

```text
reports/s1rk_four_node_fresh_manifest.json
```

S1-RK registriert keine Produktionsgeometrie, implementiert keine
Frischzustandsfabrik, importiert oder startet keinen Feldkern und fuehrt
keine Matrixzelle oder Ergebnisentscheidung aus. Der durchgefuehrte
Re-Hash-Vorgang ist ein statischer Artefaktaudit und kein Test- oder
Feldlauf.

Auditentscheidung:

```text
ALL_S1RJ_PREIMAGES_MATERIALIZED
ALL_CONFIGURATION_BINDINGS_RESOLVED
EDGE_GEOMETRY_MAPPING_AND_PUBLIC_DIGESTS_REPRODUCED
TWELVE_STATEFUL_PRIVATE_DIGESTS_REPRODUCED
TWO_STATELESS_MARKERS_PRESERVED_WITHOUT_PRIVATE_STATE
FOURTEEN_ROLE_POSITIONS_COMPLETE_AND_UNIQUE
CROSS_IDENTITY_DEPENDENCIES_MATCH
MANIFEST_DIGEST_REPRODUCED
NO_RUNTIME_NO_REGISTRATION_NO_FACTORY_NO_FIELD_EXECUTION
```

## Kanonisches Manifest

Das Manifest besitzt die Schemaidentitaet:

```text
mcm.s1rk.four-node-fresh-manifest.v1
```

Es enthaelt:

- jeden vollstaendigen S1-RJ-Praeimagepayload;
- den zugehoerigen Digest unmittelbar neben dem Payload;
- die zwei exakten Zustandslosmarkierungen;
- die 12 vollstaendigen zustandsbehafteten Privatpayloads;
- den statischen Queridentitaetsstatus;
- einen kanonischen Manifestdigest.

Der Manifestdigest wird ueber das vollstaendige Manifest ohne das Feld
`manifest_digest` gebildet. Danach wird der berechnete Wert als
`manifest_digest` eingetragen. Dadurch entsteht keine Selbstreferenz.

## Aufgeloeste Konfigurationsbindungen

Die S1-RJ-Abhaengigkeiten wurden ohne Retuning aus den bestehenden
akzeptierten Quellen aufgeloest:

| Rolle | Quelle | gebundener Digest |
|---|---|---|
| M4/DTS-1 | S1-JA DTS-1-Konfiguration | `4d7f19683f8c5b6c5ac0a62f0d9a89b9082cb325e06a9d97734c5c18efca382f` |
| B1 | S1-JA/S1-JT B1-Konfiguration | `698b6a42216915f10c40b597f40bd9cf773b845a38b35bccc176daa3362a2afa` |
| B2 | S1-JA/S1-JT B2-Konfiguration | `47915f1981d1c8220319afa6b8d819d6488dcb29ebfcba1fb2fc334b308d6dfd` |
| B3 | S1-JA/S1-JT B3-Konfiguration | `e80711e16fbac78279f5b8ab43031ff71b1adea181db15fecfb03b22551679d9` |
| B4 | S1-JA/S1-JT B4-Konfiguration | `fa36b68073f4bef8405496b1dd42cd2fd85af6d5bfedd99146efb25443ca6f06` |
| B5 | S1-JA/S1-JT B5-Konfiguration | `f7c463f8c4d167704d6c150610b2678ecac83e4df19042843b70c62253f02225` |
| B6 | S1-JA/S1-JT B6-Konfiguration | `dba608c0c01cf8b5080b6735bd71e8952fd6b3a4a382223619cda28ad832b30d` |
| B6-Spezifikation | S1-JT CONST-V-Spezifikation | `bd30dd584dd81d447aab6c55f24a99fbbdb89ad116b07ef0b831f65a41443172` |
| A3 | S1-QI NORM-Konfiguration | `3fced075e49f31608a9641d2d1a63bde2ffb1e172753faf741de669850604f2f` |
| M1 | S1-QQ Registrierung | `141b552532f0f43449e2d92c2d09274eae6acb66b224cd287b12b3a6d8d63f3b` |
| M2 | S1-QV Registrierung | `6abe7781ffd1d1b238b5e3302960b41d8e98dc880432869187f8eafdb8b95810` |
| M5 | S1-QM LEAK-Konfiguration | `788dfa1ddfd73710c0689ec6cdd06982510a45a4351b3fe59c3849476d01576c` |

A3 und M5 verwenden die bereits abgenommenen gemeinsamen technischen
Konfigurationswerte `response=1.0`, `afterimage=0.5` und keine zusaetzliche
Dissipationskonfiguration. Ihre rollenfesten W7-N-Spezifikationen bleiben
unveraendert.

## Gemeinsame Digests

| Digestrolle | Wert |
|---|---|
| Drei-Kanten-Inventar | `9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529` |
| physische Vier-Knoten-Geometrie | `e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884` |
| aeusseres Expositionsrollenmapping | `16ffec39daf424b73b94ed03b0ee4552e29372ba557b37f194c0d9499c49c1dd` |
| gemeinsame oeffentliche Frischprojektion | `ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879` |

Das Rollenmapping bleibt getrennt von der physischen Geometrie. Der
oeffentliche Frischdigest ist genau einmal vorhanden und gilt fuer alle 224
spaeteren Pflichtzellen.

## Private Frischrollen

| Position | Modellrolle | Privatdigest oder Markierung |
|---:|---|---|
| 01 | `A0_CURRENT_CONTACT` | `STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ` |
| 02 | `A1_FAST_SH` | `FIELD_ONLY:A1_FAST_SH:S1RJ` |
| 03 | `A2_B1_FIXED_ADAPTER` | `8a55ecf2cac9e4d3268eeb125cb7a6bcd2a4e79e005fbf79a381569fe30911ce` |
| 04 | `A2_B2_INTEGRATOR` | `cf1f3b36b7e47645df478c0e6099db79d199df95ef9cb0fa9f0288904928be05` |
| 05 | `A2_B3_LOCAL_LEAKY` | `89924659b50b545c17bd1734a4440764db29063f8d328719f5863d6ed230e12b` |
| 06 | `A2_B4_LINEAR_COUPLED` | `8d2a656d81d72e430d9c66611b92efc371866b65aefd530c079c67ffaa01b52e` |
| 07 | `A2_B5_F3_FULL` | `bd23b8ea5811d21c9a3abddf8622183d54b9cfb5a2aa3f0ebec8a2d5c92b3d89` |
| 08 | `A2_B6_CONST_V` | `2c7899a846853d1683aa2a0421ffda2f7cbd8951399c008a20932c0ca67edfc0` |
| 09 | `A3_NORM` | `f52e3304538891ed7f9b9eb7ca8d3bbfc79bbf8284ac506f6496ad7052ab2ab4` |
| 10 | `M1_PARALLEL_LEAK` | `c84829037970255ca0e16417cae9001938a5a50843cc416325c0a9f44963afc5` |
| 11 | `M2_DELAY` | `97ff90b67e001ba3346173f8a1df7620a5b2895022df14947f34142595f03ea0` |
| 12 | `M2_REPLAY` | `5fc1d98b534e5a6fbe13afe6913e86011ceed7b2b1f94be7c9abb375aaa08be7` |
| 13 | `M4_DTS1_T1` | `c673984c64f88074d276f4430e92a4b9242f1118d47eaa85d4a776f405169b2f` |
| 14 | `M5_DIRECT` | `7eed04ea4fbc72d8c7370ee96ee2a509b9384bc9ec19be54cc533b8f89434edc` |

Die 12 Privatdigests sind rollenverschieden. Das ist erwartet und notwendig.
A0 und A1 bleiben ohne kuenstlichen Privatpayload.

## Manifestdigest

Der kanonische Gesamtmanifestdigest lautet:

```text
ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68
```

Der Wert wurde beim unabhaengigen Re-Hash der gespeicherten Datei exakt
reproduziert.

## Queridentitaetsaudit

Der statische Audit bestaetigt:

- alle vier gemeinsamen Payloaddigests reproduzieren sich;
- alle 12 privaten Payloaddigests reproduzieren sich;
- die zwei Zustandslosmarkierungen stehen an Position 01 und 02;
- die 14 Rollenpositionen bilden lueckenlos `01` bis `14`;
- B1, B3-B6 und M4 referenzieren denselben Kanteninventardigest;
- Geometrie, Rollenmapping, oeffentliche Projektion und M2-Zustaende
  referenzieren denselben physischen Geometriedigest;
- der oeffentliche Frischpayload enthaelt vier Nullknoten und keinen privaten
  Status;
- alle Konfigurationsbindungen sind aufgeloest;
- die Digestabhaengigkeiten sind azyklisch;
- der Manifestdigest reproduziert sich nach Entfernen seines eigenen Feldes.

Es gab keine Reparatur, Toleranz, Alternativserialisierung oder
Ergebnisabhaengigkeit.

## Technische Grenze

S1-RK belegt nur, dass der statische Vier-Knoten-Frischbestand vollstaendig,
kanonisch und reproduzierbar beschrieben ist. Es belegt nicht, dass:

- die Geometrie durch den produktiven Feldkern erzeugt werden kann;
- die 14 Frischfabriken oder Adapterhuellen implementiert sind;
- eine Pflichtmatrixzelle ausfuehrbar ist;
- eine Baseline anschlussfaehig oder funktional ausreichend ist;
- eine hypothetische MCM-Memory vorliegt.

## Fail-Closed-Regeln

Der S1-RK-Stand wird verletzt, wenn spaeter:

- das Manifest ohne neue Vertragsstufe veraendert wird;
- ein gespeicherter Payload seinen Digest nicht reproduziert;
- der Manifestdigest ueber sich selbst oder eine anders formatierte Datei
  berechnet wird;
- eine Konfigurationsbindung gegen einen neuen Wert ausgetauscht wird;
- Rollenmapping in Modell- oder Geometriepayload gelangt;
- A0 oder A1 einen Privatdigest erhalten;
- verschiedene Frischrepliken denselben veraenderlichen Objektstatus teilen;
- die statische Manifestabnahme als Feld- oder Funktionsbefund ausgegeben
  wird;
- Produktionsregistrierung oder Fabrikimplementierung ohne eigenen
  Einfuegepunkt- und Abnahmevertrag beginnt.

## Paketstatus

```text
S1RJ_FRESH_MANIFEST_MATERIALIZED
ALL_BOUND_DIGESTS_REPRODUCIBLE
CROSS_IDENTITIES_ACCEPTED
PRODUCTION_GEOMETRY_NOT_REGISTERED
FRESH_FACTORIES_NOT_IMPLEMENTED
BASELINE_WRAPPERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RL - statischer Registrierungs-, Frischfabrik-, Manifestconsumer- und
        technischer Abnahmebudgetvertrag
```

S1-RL soll ausschliesslich festlegen, an welchen bestehenden Modulen die
Vier-Knoten-Geometrie, der unveraenderliche Manifestconsumer und die 14
Frischrollen angeschlossen werden duerfen. Es muss Dateibudget, API-Grenzen,
Fail-Closed-Fehler, Objekttrennung und fokussierte technische Tests binden.
Noch keine Implementierung, keine Registrierung, keine Testausfuehrung,
keine Matrixzelle und kein Feldlauf.
