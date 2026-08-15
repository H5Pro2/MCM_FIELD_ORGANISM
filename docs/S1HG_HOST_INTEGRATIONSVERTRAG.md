# S1-HG: Host-Integrationsvertrag

Stand: 2026-08-15

Status: `HOST_ANFORDERUNGEN_GEBUNDEN_EXTERNER_PROVIDER_FEHLT`

## Ergebnis

S1-HG bindet die kleinste zulaessige Uebergabe zwischen Forschungsrepository
und einem spaeteren vertrauenswuerdigen Orchestrator-/Host-Provider.

Der Host muss zwei zusammengehoerende Belege liefern:

1. ein authentifiziertes Besitzerereignis mit Principal-, Nachrichten-,
   Session-, Reihenfolge-, Nonce-, Gate- und Zielbindung;
2. eine nicht exportierbare Einmal-Capability, die an genau dieses Ereignis,
   die daraus entstandene Autorisierung, das S1-GY-Ziel und den festgelegten
   Produktionskernel gebunden ist.

Die Capability darf nur innerhalb der Hostgrenze verbraucht werden. Direkt
danach sind genau ein Produktionskernel-Aufruf und ein Feldschritt erlaubt.
Erfolg oder Fehler muessen die Capability beenden; geliefert wird ein
vollstaendig attestiertes Ergebnis oder kein Ergebnis.

## Nicht ersetzbare Grenze

Ein lokaler Callback, ein Python-Objekt, Nachrichtentext oder ein weiterer
Digest kann weder Host-Herkunft noch Capability-Besitz beweisen. Das
Repository besitzt weiterhin keinen solchen Provider und implementiert in
S1-HG weder Verifier noch Capability-Factory oder Produktionskernel-Pfad.

Entscheidung:

```text
HOST_INTEGRATION_REQUIREMENTS_BOUND_EXTERNAL_PROVIDER_ABSENT
```

Es wurde keine Autorisierung angefragt, keine Capability erzeugt, kein Token
erstellt und kein Feldschritt ausgefuehrt. Dies ist eine Workflow-
Sicherheitsgrenze und kein MCM-, Substrat- oder Memory-Befund.

## Bester naechster Schritt

Der produktive Realpfad kann im Forschungsrepository nicht normal lokal
fortgesetzt werden. Als naechster Schritt muss der Codex-Workflow-
Orchestrator oder ein anderer Host den hier gebundenen Provider tatsaechlich
implementieren. Bis dessen konkrete Schnittstelle vorliegt, bleibt dieser
Realpfad geschlossen; die kontrollierte synthetische AV-/Feld-Engineeringlinie
kann unabhaengig davon weiterlaufen.
