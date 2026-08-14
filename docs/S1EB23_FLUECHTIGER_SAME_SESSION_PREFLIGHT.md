# S1-EB23: Fluechtiger Same-session-Preflight

## Status

S1-EB23 implementiert das letzte technische Vorlaufgate fuer den einmalig
autorisierten S1-EB-Bestaetigungslauf. Das Gate wird ausschliesslich im
Arbeitsspeicher erzeugt, ist an den aktuellen Prozess gebunden und hoechstens
fuenf Sekunden gueltig.

Der kanonische Lauf wurde nicht gestartet. Es wurden keine S1-EB-Zieldateien
angelegt und keine Forschungsentscheidung getroffen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_same_session_preflight.py
tests/test_e1_confirmation_same_session_preflight.py
```

Normalisierter Implementierungsdigest:

```text
aa5898f7e8b8dedb49459bd87b5c011d84a4930bfd99608b17ba699a1f087151
```

## Gebundene Voraussetzungen

Der Preflight prueft in derselben Sitzung erneut:

```text
S1-EB9-Produzentenbindung und S1-EB-Kettenvertrag
S1-EB19-Releasevertrag
S1-EB20-Prueferfreigabe als gebundene Datei
S1-EB21-Projekteigner-Autorisierung
S1-EB22-Ressourcenwaechter
alle kanonischen Adapter- und Executor-Digests
S1-EA6-Berichtsdigest
freie und voneinander verschiedene S1-EB-Zielpfade
23800 Feldschritte
1800 Sekunden Wandzeit
4 GiB jobweiter Speicherdeckel
No-Retry und genau ein autorisierter Lauf
```

## Fluechtige Freigabeoberflaeche

Nur ein intaktes Receipt mit folgenden Eigenschaften oeffnet das technische
Gate:

```text
process_id = aktueller Prozess
max_age_ns = 5000000000
preflight_status = READY_FOR_IMMEDIATE_ONE_SHOT
canonical_execution_permitted = true
canonical_persistence_permitted = true
claims_permitted = false
```

Das Receipt ist keine dauerhaft gespeicherte Freigabe. Ein spaeterer
Executor darf kein zuvor erzeugtes Receipt wiederverwenden, sondern muss es
innerhalb seines eigenen Workerprozesses unmittelbar vor dem ersten
Exactly-once-Marker neu erzeugen und sofort verbrauchen.

## Technische Abnahme

```text
6 fokussierte S1-EB23-Tests
566 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden das enge Laufgate, die Bindung von Autorisierung und
Ressourcenlimits, Fail-closed bei abgelaufenem Receipt oder anderer
Prozessidentitaet, die Fluechtigkeit zweier Receipts sowie das Ausbleiben von
Runtime- und Schreibaufrufen.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Aussagegrenze

S1-EB23 weist nur nach, dass die bereits fachlich freigegebenen technischen
Voraussetzungen unmittelbar vor einem moeglichen Einmallauf geschlossen
erneut geprueft werden koennen. Das ist kein Memory-, Feldzeit-, Bedeutungs-,
Organisations-, Topologie- oder KI-Nachweis.

## Bester naechster Schritt

S1-EB24 implementiert den freigegebenen Einmal-Worker und seine synthetische
Orchestrierungsabnahme. Der Worker muss S1-EB23 intern unmittelbar vor dem
ersten Exactly-once-Marker neu erzeugen und konsumieren und unter dem
S1-EB22-Job-Object-Waechter laufen. Die synthetische Abnahme darf den
kanonischen S1-EB-Lauf noch nicht starten.
