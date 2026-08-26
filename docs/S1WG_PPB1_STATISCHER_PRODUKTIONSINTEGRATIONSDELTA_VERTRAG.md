# S1-WG: Statischer PPB-1-Produktionsintegrationsdelta-Vertrag

## Auftrag und Grenze

S1-WG beschreibt ausschliesslich die Differenz zwischen dem nach S1-WF
vorhandenen privaten Testbestand und einer spaeter moeglichen kontrollierten
Produktionsintegration. Der Vertrag fuegt keine Runtime hinzu.

Unzulaessig bleiben:

- Koordinatorimplementierung;
- Autorisierungsinstanziierung;
- Ressourcenabfrage oder Dateischreibvorgang;
- Aufloesung oder Aufruf des privaten realen Producers;
- registrierter Matrixpfad oder Produktionsartefakt;
- Feld- oder Medienruntime.

## Sechs Integrationsdeltas

Der kanonische Vertrag bindet exakt:

```text
PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED
  -> S1WGProductionResourceObserverAdapter

PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED
  -> S1WGExactProductionAuthorizationActivator

PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED
  -> S1WGProductionLockTerminalAdapter

PRIVATE_REAL_PRODUCER_NOT_BOUND
  -> S1WGPrivateS1VQProducerResolver

PRODUCTION_ARTIFACT_PATH_NOT_WIRED
  -> S1WGProductionArtifactRootResolver

PRODUCTION_ENTRYPOINT_HARD_BLOCKED
  -> S1WGPrivateProductionCoordinator
```

Jede Rolle besitzt im JSON-Vertrag eine eigene Vorbedingung,
Integrationswirkung und Stoppregel. Keine Rolle darf durch Umbenennung einer
vorhandenen Temporaerfunktion als geschlossen gelten.

## Kausale Unterordnung

H0 bleibt in fuenf feste Pruefungen zerlegt. Erst nach Vertrag, Plan,
Plattform, Quellen, Produktionswurzel, unmittelbaren Ressourcen,
Autorisierung und erneut freien Artefaktpfaden darf H1 den dauerhaften Lock
erzeugen.

Die Referenz des privaten S1-VQ-Producers darf nicht vorher importiert,
aufgeloest oder aufgerufen werden. Erst der erfolgreiche H1-Lock dominiert
die einmalige H2-Aufloesung und den Aufruf. Fehler nach H1 erzeugen nur einen
terminalen Fehler, lassen den Lock bestehen und verbieten Retry.

Erfolg und Fehler bleiben gegenseitig ausschliesslich. Die atomare
Terminalpublikation darf ein vorhandenes Ziel nicht ersetzen. Matrix-,
Kompositions- oder Auswertungsteilresultate werden weder separat gespeichert
noch zurueckgegeben.

## Autorisierungsgrenze

Eine spaetere Autorisierung muss gleichzeitig binden:

- eine frische, bisher unbenutzte Ausfuehrungs-ID;
- den S1-WA-Vertragsdigest;
- den S1-VZ-Kalibrierungsdigest;
- den unmittelbar zuvor erzeugten Ressourcengatedigest;
- die gebundenen Plaene, Budgets und den privaten Entry.

Allgemeine Befehle wie `ok weiter`, fruehere Autorisierungen und die
Textvorlage selbst sind keine reale Autorisierung. Eine gueltige Freigabe
waere vor der ersten Produceraufloesung dauerhaft zu verbrauchen und duerfte
nicht wiederverwendet werden.

## Kanonische Bindung

```text
Vertragsdatei:
S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json

Vertragsdigest:
c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b

Parent-Preflightdigest:
bdd1f9652ac2cd094d794c4a589a2eeae90ca5357f5ccf34863f1368e99c96af
```

Die acht neuen Tests pruefen Digest, Parentbindungen, Budgets, sechs
eindeutige Deltas, H0-H7-Reihenfolge, Autorisierungsgrenze,
Producerunterordnung, Lock-/Terminalregeln und vollstaendige
Ausfuehrungsverbote. Zusammen bestehen `221 von 221` aktuelle fokussierte
PPB-1-Tests.

## Entscheidung

```text
S1_WG_EXACT_SIX_PRODUCTION_INTEGRATION_DELTAS_BOUND
S1_WG_EXACT_H0A_TO_H0E_AND_H1_TO_H7_ORDER_PRESERVED
S1_WG_PRODUCER_RESOLUTION_STRICTLY_AFTER_DURABLE_H1_BOUND
S1_WG_EXACT_FRESH_AUTHORIZATION_BOUND_GENERIC_COMMANDS_EXCLUDED
S1_WG_ATOMIC_NO_REPLACE_TERMINAL_AND_NO_PARTIAL_RESULTS_BOUND
S1_WG_ZERO_IMPLEMENTATION_AND_RUNTIME_EFFECTS
S1_WG_8_OF_8_NEW_TESTS_PASS
S1_WG_221_OF_221_CURRENT_FOCUSED_PPB1_TESTS_PASS
```

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WH - private Integrationsrollentypen und fail-closed Koordinatorhuelle
        mit ausschliesslich injizierten Testadaptern
```

S1-WH darf nur Typen, Reihenfolgevalidator und eine nicht produktiv
erreichbare Koordinatorhuelle implementieren. Produktionswurzel,
Autorisierungsaktivierung, realer Producer, Produktionsentry, Matrix-, Feld-
und Medienlauf bleiben gesperrt.

## Grundlagen

- [Kanonischer S1-WG-Vertrag](S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json)
- [S1-WF statischer Rollen- und Integrationspreflight](S1WF_PPB1_STATISCHER_ROLLEN_UND_INTEGRATIONSPREFLIGHT.md)
- [S1-WA Produktionsbindungs- und Autorisierungsvertrag](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md)
