# W7-AN: Private Materialisierungs- und Audittrennstelle

## Entscheidung

`W7AN_PRIVATE_MATERIALIZATION_AUDIT_BOUNDARY_IMPLEMENTED_R1_COMPATIBLE`

W7-AE und W7-AG besitzen jetzt private Zwischenobjekte und getrennte
Funktionen fuer kanonische Materialisierung und Gegenkontrollaudit. Die
oeffentlichen Funktionen fuehren weiterhin beide Phasen unmittelbar
nacheinander aus.

## W7-AE

`_materialize_w7ae_cap_paths(...)` erzeugt ausschliesslich die sieben
kanonischen CAP-Pfade mit 67 Produktionen. Das private unveraenderliche
Zwischenobjekt bindet Plan, P0, Observer, Anfangsfeld, Refinement und die
geordneten Pfadresultate.

`_audit_w7ae_cap_materialization(...)` akzeptiert nur dieses gebundene
Zwischenobjekt, fuehrt die bisherigen Pfad- und Haupt-/Probe-
Gegenkontrollen aus und erstellt danach das unveraenderte oeffentliche
W7-AE-Ergebnis.

## W7-AG

`_materialize_w7ag_measurements(...)` erzeugt ausschliesslich die 35
kanonischen Messresultate. Das private Zwischenobjekt bindet Plan,
CAP-Gesamtdigest, Refinement und die geordnete Rollenmenge.

`_audit_w7ag_measurements(...)` fuehrt danach die 35 umgekehrten
Messwiederholungen und die eine Observerpassivitaetskontrolle aus und
erstellt das unveraenderte oeffentliche W7-AG-Ergebnis.

## Kompatibilitaet

Sechs neue private Grenztests und die sieben Tests der statischen
Ausfuehrungszerlegung bestehen gemeinsam mit `13 tests, OK`. Zusaetzlich
wurde die bestehende reale R1-W7-AG-Suite ausgefuehrt:

```text
10 tests, OK
343.591 Sekunden
W7-AG-Digest:
898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8
```

Damit bleibt der bisherige oeffentliche R1-Pfad bitgleich. Die neuen
Funktionen und Zwischenobjekte sind privat und nicht in `current_api`
exportiert.

## Offene Trennstelle

Die Auditfunktionen sind inzwischen vollstaendig auf 67+4 fuer W7-AE und
35+1 fuer W7-AG geteilt. Offen ist nun der private stufenweise W7-AN-
Executor, der alle sechs Phasen je Aufloesung verbindet und erst danach ein
Resultat finalisiert.

## Grenzen

- Kein R2- oder R4-Vollpfad wurde ausgefuehrt.
- Kein Gesamtcontainerdigest und kein 306-Zeugen-Nachweis liegt vor.
- Kein Browser, Report oder Forschungslauf wurde gestartet.
- Keine Konvergenz oder Schwelle wurde berechnet.
- Daraus folgt kein Funktions-, Memory-, Feldzeit-, Organisations- oder
  KI-Befund.
