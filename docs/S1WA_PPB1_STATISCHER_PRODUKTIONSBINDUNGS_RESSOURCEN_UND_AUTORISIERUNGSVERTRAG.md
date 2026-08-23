# S1-WA: Statischer PPB-1-Produktionsbindungs-, Ressourcen- und Autorisierungsvertrag

## Auftrag und Grenze

S1-WA bindet nach der S1-VZ-Kalibrierung die spaetere private
Produktionsarchitektur. Der kanonische Vertrag liegt hier:

[S1-WA Produktionsvertrag v1](S1WA_PPB1_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG_V1.json)

S1-WA implementiert keinen Typ und keinen Entry. Es fragt keine Ressource ab,
rendert keinen gueltigen Autorisierungstext, erzeugt kein
Produktionsartefakt und ruft keinen privaten oder oeffentlichen Runner auf.

## Gebundene Grundlage

Verbindlich bleiben:

```text
Faelle:                         528
maximale registrierte Aufrufe:  75.808
freier physischer Speicher:     mindestens 2.147.483.648 Bytes
freies Artefaktvolume:          mindestens 1.073.741.824 Bytes
Produktionsartefaktwurzel:      data/generated/ppb1/one_shot
```

Plattform und kalibrierte S1-VQ-, S1-VT-, S1-VW- und S1-VZ-
Quellcodedigests muessen bitgleich mit S1-VZ bleiben. Jede Abweichung
verwirft die Kalibrierung und verlangt vor einer neuen Produktionsfreigabe
eine neue synthetische Kalibrierung.

## Private Produktionstypen

Eine spaetere Implementierung muss genau diese getrennten Rollen besitzen:

```text
S1WAProductionResourceObservation
S1WAProductionResourceGate
S1WAProductionAuthorization
S1WAProductionLockMarker
S1WAProductionSuccessOutcome
S1WAProductionErrorOutcome
```

Keiner dieser Typen darf in Paket-Root, `current_api`, Feldsnapshot oder
Medienruntime exportiert werden.

## Unmittelbare Ressourcenbeobachtung

Die Ressourcenbeobachtung wird spaeter nur innerhalb von H0 und unmittelbar
vor dem Autorisierungsverbrauch erzeugt. Sie bindet:

- aktuelle Plattform- und Quellcodedigests;
- aktuell frei verfuegbaren physischen Speicher;
- freien Speicherplatz auf dem Produktionsartefaktvolume;
- Volumeidentitaet von Temporaer- und Terminalpfad;
- Same-Volume-Eigenschaft;
- erfolgreichen atomaren Replace-Probelauf;
- freie Lock-, Success-, Error- und Temporaerpfade;
- kanonischen Beobachtungsdigest.

Der atomare Probelauf verwendet nur eigene, an die Ausfuehrungs-ID gebundene
Probe-Dateien im Git-ignorierten Produktionsverzeichnis. Er muss vor H1
vollstaendig abgeschlossen und entfernt sein. Ein verbliebener Probepfad
stoppt H0.

## Produktions-Ressourcengate

Das Gate verbindet Beobachtung, S1-VY-Vertrag und S1-VZ-Kalibrierung. Es
weist jede Einzelpruefung separat aus:

- mindestens `2 GiB` aktueller freier physischer Speicher;
- mindestens `1 GiB` aktueller freier Speicherplatz;
- bitgleiche Plattform;
- bitgleiche kalibrierte Quellcodedigests;
- Temporaer- und Terminalpfad auf demselben Volume;
- bestandener atomarer Replace-Probelauf;
- freie Produktionsartefaktpfade.

Nur wenn alle Rollen bestehen, entsteht
`all_resource_gates_passed = true` mit einem kanonischen
Ressourcengatedigest. Der Gatebeleg gilt nur fuer dieselbe Ausfuehrungs-ID
und denselben unmittelbar folgenden H1-Verbrauch.

## Autorisierungsvorlage

S1-WA bindet nur eine Vorlage, noch keinen gueltigen Freigabetext:

```text
Ich autorisiere genau einen realen PPB-1-Korrekturmatrixlauf mit 528 Faellen
und maximal 75.808 registrierten Aufrufen fuer die Ausfuehrungs-ID
{execution_id}, gebunden an den S1-WA-Vertragsdigest {contract_digest}, den
S1-VZ-Kalibrierungsdigest
e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928 und
den unmittelbar bestandenen Ressourcengatedigest {resource_gate_digest}. Die
Freigabe wird vor dem ersten Aufruf dauerhaft verbraucht; ein Retry ist nicht
erlaubt.
```

Die Platzhalter duerfen erst ein spaeter bestandener Post-Implementierungs-
Preflight einsetzen. Der gerenderte Text muss Zeichen fuer Zeichen stimmen
und gemeinsam mit Ausfuehrungs-ID, Plan-, Vertrags-, Kalibrierungs-,
Ressourcen- und Entry-Digests im typisierten Autorisierungsobjekt gebunden
sein.

Der gegenwaertige Befehl `ok weiter`, fruehere Freigaben und die Vorlage
selbst sind keine reale Autorisierung.

## Feste Produktionsreihenfolge

Vor H1 gilt genau diese H0-Unterordnung:

```text
H0A Vertrag, Plaene, Plattform und Quellcodedigests pruefen
H0B Produktionswurzel, Same-Volume und atomaren Replace pruefen
H0C aktuellen Speicher und Datentraeger beobachten, Ressourcengate bilden
H0D exakt gerenderte Autorisierung und unbenutzte Ausfuehrungs-ID pruefen
H0E freie Lock-, Success-, Error- und Temporaerpfade bestaetigen
```

Danach bleibt die S1-VV-Reihenfolge verbindlich:

```text
H1 Lock exklusiv anlegen und Autorisierung dauerhaft verbrauchen
H2 privaten S1-VQ-Produzenten genau einmal aufrufen
H3 vollstaendiges altes S1-VQ-Resultat validieren
H4 exakt 528 Receipts mit S1-VT versiegeln
H5 exakt 48 Armrecords und Evidenzledger komponieren
H6 S1-VT-v2-Auswerter genau einmal anwenden
H7 genau ein terminales Erfolgs- oder Fehlerartefakt atomar publizieren
```

Der private S1-VQ-Koerper ist der einzige zulaessige Producer. Seine Referenz
darf vor erfolgreichem H1 nicht aufgerufen werden. S1-VO-v1, Teilresultate,
Retry, Lockloeschung und Systemzeit als kausale oder Digestrolle bleiben
verboten.

## Fail-Closed-Regeln

Jeder Fehler in H0 stoppt mit Nullstart: keine verbrauchte Autorisierung,
kein Lock und kein Produceraufruf. Jeder Fehler nach H1 erzeugt nur ein
terminales Fehlerobjekt ohne Teilresultat; der Lock bleibt bestehen und ein
Retry ist verboten.

Erfolg und Fehler sind gegenseitig ausschliesslich. Temporaer- und
Terminalartefakt muessen im selben Verzeichnis und auf demselben Volume
liegen.

## Kanonische Bindung

```text
S1-VZ-Kalibrierungsdigest:
e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928

S1-WA-Vertragsdigest:
e1d6c99f9141140c7db207513e725d3521065bab488d7541d4392db0b5218413
```

Der S1-WA-Digest wird aus dem JSON-Inhalt mit sortierten Schluesseln und
kompakten UTF-8-Trennzeichen gebildet. Es wurden keine Tests oder
Ausfuehrungsfunktionen gestartet.

## Entscheidung

```text
S1_WA_EXACT_PRIVATE_PRODUCTION_TYPES_BOUND
S1_WA_IMMEDIATE_H0_RESOURCE_OBSERVATION_BOUND
S1_WA_CALIBRATED_2_GIB_MEMORY_AND_1_GIB_DISK_GATES_BOUND
S1_WA_SAME_VOLUME_ATOMIC_REPLACE_AND_FREE_PATH_GATES_BOUND
S1_WA_AUTHORIZATION_TEMPLATE_WITH_LATE_DIGEST_RENDERING_BOUND
S1_WA_EXACT_H0A_TO_H0E_AND_H1_TO_H7_ORDER_BOUND
S1_WA_PRIVATE_S1VQ_BODY_AS_ONLY_PRODUCER_BOUND
S1_WA_ZERO_START_AND_NO_RETRY_RULES_BOUND
S1_WA_NO_SYSTEM_TIME_ROLE_BOUND
S1_WA_NO_IMPLEMENTATION
S1_WA_NO_RESOURCE_OBSERVATION
S1_WA_NO_AUTHORIZATION_RENDERING
S1_WA_NO_MATRIX_EXECUTION
```

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WB - private Produktionsrollen- und H0-Gate-Implementierung mit
        synthetischen Beobachtungsfixtures
```

S1-WB darf nur die Produktionsressourcen-, Gate- und Autorisierungstypen
sowie reine H0-Validatoren implementieren. Ressourcenwerte und
Dateisystempruefungen muessen injiziert und synthetisch bleiben. Der reale
S1-VQ-Producer darf noch nicht gebunden oder aufgerufen, der
Produktionsentry nicht geoeffnet und kein Produktionsartefakt erzeugt
werden.

## Grundlagen

- [S1-VZ synthetische Ressourcenkalibrierung](S1VZ_PPB1_PRIVATE_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_UND_GATEABNAHME.md)
- [S1-VY Ressourcenmess- und Gatevertrag](S1VY_PPB1_STATISCHER_PRODUKTIONS_RESSOURCENMESS_UND_GATEVERTRAG.md)
- [S1-VV Einmallauf- und Handoffvertrag](S1VV_PPB1_STATISCHER_EINMALLAUF_HANDOFF_ERGEBNIS_UND_FEHLERVERTRAG.md)
