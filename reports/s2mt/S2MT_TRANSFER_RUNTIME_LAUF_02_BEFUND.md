# S2-MT: Transferlauf 02

## Entscheidung

Der einmalige Lauf `s2mt-presealed-transfer-runtime-20260905-02` ist
`NOT_EVALUABLE`.

Der Fehlerbeleg lokalisiert den technischen Abbruch auf die Phase
`MATERIALIZATION`. Es wurden keine Runtimeinstanz und kein fachlich
auswertbarer Transferpfad erreicht. Der Lauf ist deshalb weder eine
Bestaetigung noch eine Falsifikation der S2-MR-Transferfrage.

## Gebundener Umfang

- unveraenderter vorversiegelter Korpus;
- 28 neutrale Ereignisspezifikationen;
- 20 vorgesehene Formationen und acht vorgesehene Teilhinweise;
- 8.064 vorgesehene Feldkontakte;
- unveraenderte S2-MR-Runtime, Schwellen und Auswertungsregeln;
- genau ein Hauptaufruf und eine read-only Verifikation;
- kein Retry oder Parameterwechsel.

Der Korpusquellhash blieb gegenueber Lauf 01 unveraendert:
`ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`.

## Fehlerbeleg

Der kompakte `S2MTFailureReceiptV1` bindet:

- Phase: `MATERIALIZATION`;
- Fehlercode: `S2MT_MATERIALIZATION_FAILED`;
- aktuelle Ereignisordinalzahl: `None`;
- vollstaendig abgeschlossene Ereignisse: `0`;
- letzter gueltiger Runtime-Snapshot-Digest: `None`;
- Failure-Receipt-Digest:
  `4bf0b56132af567321216800ff5fbc03065105aacc287095408d7389bc6b03a4`.

`execution` und `evaluation` sind beide `null`. Damit ist keine teilweise
fachliche Auswertung vorhanden. Die gebundene Phase umfasst die private
Ereignismaterialisierung, deren Geometrieprojektion und das zugehoerige
Materialisierungsgate; der abgeschlossene Beleg bindet absichtlich keine
Exceptiontexte oder feinere Ursachenunterstufe.

## Lauf und Verifikation

Der Hauptaufruf wurde genau einmal ausgefuehrt, verbrauchte die Einmalmarke
und setzte das Gate wieder auf `False`.

Ergebnisdatei:

- Groesse: 2.520 Byte;
- Datei-SHA-256:
  `d05459dc79e1933117bf7db4ea1ff34cf41486365f6a54c47dc723ee37000d79`;
- Record-Digest:
  `5dee00e5e7343cd1f14ae0dabf6f2a86c6c301a7cc65955122675f269d9ad9f2`.

Die genau einmal ausgefuehrte unabhaengige read-only Verifikation bestaetigte
die kanonische Ergebnisform, Quellenbindungen, Fehlerphase, Fortschrittsform
und Digests:

- Verifikationsstatus: `NOT_EVALUABLE`;
- Read-only: `true`;
- Verifikationsdigest:
  `7ffa62aa47a4c104e22ee1c886e9cff97e563a06f472aadebd0f33df3ece93c5`.

Der fruehere Lauf `s2mt-presealed-transfer-runtime-20260905-01` bleibt
unveraendert `NOT_EVALUABLE`. A/B-Stabilisierung, C-Instabilitaet,
Verdraengung und Hypothesenausgabe wurden in Lauf 02 nicht ausgewertet.
