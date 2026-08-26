# W7-AN: Vollstaendige private Auditbatchgrenzen

## Entscheidung

`W7AN_PRIVATE_67_4_35_1_AUDIT_BOUNDARIES_IMPLEMENTED_R1_COMPATIBLE`

Die Gegenkontrollaudits von W7-AE und W7-AG sind jetzt entlang der statisch
gebundenen Integrationsinventare getrennt. Die bestehende oeffentliche
Komposition bleibt unveraendert.

## W7-AE

Die private Auditphase besteht aus:

- `_audit_w7ae_path_order(...)`: 67 Integrationen fuer die umgekehrte
  Pfadreihenfolge;
- `_audit_w7ae_branch_order(...)`: 4 Integrationen fuer die Haupt-/Probe-
  Reihenfolge;
- `_finalize_w7ae_countercontrols(...)`: reine Validierung und Komposition
  des bisherigen `W7AECAPCountercontrols`-Objekts ohne Integration.

Beide Auditobjekte binden ihren Refinementfaktor. Eine Finalisierung mit
Auditobjekten verschiedener Aufloesungen wird verworfen.

## W7-AG

Die private Auditphase besteht aus:

- `_audit_w7ag_measurement_order(...)`: 35 Integrationen fuer die
  umgekehrte Messreihenfolge;
- `_audit_w7ag_observer_passivity(...)`: 1 Integration fuer die
  Observerpassivitaet;
- `_finalize_w7ag_measurement_audits(...)`: reine Validierung und
  Komposition des bisherigen W7-AG-Handoffs ohne Integration.

Auch hier muessen Materialisierung, Reihenfolgeaudit und Passivitaetsaudit
denselben Refinementfaktor binden.

## Technische Pruefung

Der schnelle Verbund aus Batch-, Phasen- und Zerlegungstests besteht:

```text
18 tests, OK
```

Die reale R1-W7-AG-Suite baut W7-AE und W7-AG vollstaendig auf und besteht:

```text
10 tests, OK
342.151 Sekunden
W7-AG-Digest:
898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8
```

Damit bleiben die bisherigen R1-Ergebnisobjekte und Digests nach der
feineren privaten Teilung bitgleich. Keine neue Funktion ist in
`current_api` exportiert.

## Offener W7-AN-Schritt

Die sechs Phasen je Aufloesung sind nun einzeln aufrufbar:

```text
67 CAP-Materialisierung
35 Messmaterialisierung
67 CAP-Pfadreihenfolge
4 CAP-Branchreihenfolge
35 Messreihenfolge
1 Observerpassivitaet
```

Der private stufenweise Executor ist implementiert und hat die einmalige
reale R1-Kompatibilitaetsausfuehrung gegen die kanonischen W7-AE-, W7-AG-
und W7-AK-Digests bestanden. Offen ist der statische Gesamtkoordinator vor
R2 und R4.

## Grenzen

- Kein R2- oder R4-Vollpfad wurde ausgefuehrt.
- Kein W7-AN-Gesamtcontainerdigest liegt vor.
- Die 306 Zeugen sind noch nicht vollstaendig materialisiert.
- Kein Browser, Report oder Forschungslauf wurde gestartet.
- Keine Konvergenz, Schwelle oder Feldfunktion wurde ausgewertet.
- Daraus folgt kein Memory-, Feldzeit-, Organisations- oder KI-Befund.
