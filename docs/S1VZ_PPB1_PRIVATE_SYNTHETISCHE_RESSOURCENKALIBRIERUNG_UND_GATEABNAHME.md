# S1-VZ: Private synthetische PPB-1-Ressourcenkalibrierung und Gateabnahme

## Auftrag und Grenze

S1-VZ implementiert den privaten Ressourcen-Kalibrierer aus S1-VY und
fuehrt genau eine gueltige Serie aus drei frischen synthetischen
Workerprozessen `R1`, `R2` und `R3` aus.

Jeder gueltige Worker konstruiert 528 Receiptrollen mit 75.808 typisierten
Beobachtungen und fuehrt sie ueber die private synthetische S1-VW-Handoff-
und S1-VT-Ergebnispipeline. Kein registrierter S1-VQ-Pfad, kein realer
Producer, kein Produktionsartefakt und keine Feld- oder Medienruntime wird
verwendet.

Das kanonische Messergebnis liegt hier:

[S1-VZ Kalibrierresultat v1](S1VZ_PPB1_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_RESULT_V1.json)

## Implementierter Kalibrierer

Das private Modul
[`_ppb1_s1vz_synthetic_resource_calibration.py`](../mcm_field_organism/_ppb1_s1vz_synthetic_resource_calibration.py)
implementiert:

- feste Drei-Prozess-Orchestrierung ohne Wiederholungs- oder Schleifenwahl;
- synthetische 528-Receipt-Fixture innerhalb des gebundenen Quellmoduls;
- native Windows-Prozess-RSS- und Peak-RSS-Messung;
- Stufenmessungen nach Fixture, Versiegelung, Komposition, Auswertung und
  Serialisierung;
- Lock-, Erfolgs- und Temporaerartefaktgroessen;
- freien Speicherplatz vor und nach jeder Replik;
- atomaren Same-Volume-Replace im temporaeren Testbereich;
- reine Maximalwertaggregation und die S1-VY-Gateformeln;
- harte Produktionssperre.

## Gueltige Messserie

Alle drei Repliken verwenden bitgleich:

```text
Python:              CPython 3.14.4
Betriebssystem:      Windows
Architektur:         AMD64 / 64 Bit
S1-VQ-Digest:        c9485bf36e6bec241ac3e0c565e7b5d5ec7fc4041596557f2e3db26ecb757c48
S1-VT-Digest:        0aeba24aac5732f11500ec02f51aded07097c0e58c54b05a9f6978ff6980b891
S1-VW-Digest:        37ea1c2a76b1a987dc72a3999162cd730484a75a5a3cdf60f04d6562320322f0
S1-VZ-Digest:        8ef0268fe3e1c5d9eac1e85092f21854ed7a09992e79dbf9e8efd1066d5c42f5
```

Gemessene RSS-Zuwaechse:

```text
R1: 195.739.648 Bytes
R2: 197.292.032 Bytes
R3: 195.878.912 Bytes

Maximum: 197.292.032 Bytes (rund 188,15 MiB)
```

Alle drei Erfolgs- und Temporaerartefakte besitzen jeweils
`34.834.914 Bytes` (rund `33,22 MiB`). Jeder Same-Volume-Replace-Test
besteht. Die drei Terminaldigests sind getrennt und die Plattform- sowie
Quellbindungen sind bitgleich.

## Abgeleitete Produktionsuntergrenzen

Nach den in S1-VY gebundenen Formeln ergeben sich:

```text
minimum_free_memory_bytes = 2.147.483.648  (2 GiB)
minimum_free_disk_bytes   = 1.073.741.824  (1 GiB)
```

In beiden Faellen dominiert die feste Sicherheitsuntergrenze den aus den
Messwerten berechneten Faktor. Diese Werte gelten nur fuer die exakt
gebundene Plattform und die vier gebundenen Quellcodedigests. Jede Aenderung
macht die Kalibrierung fuer ein spaeteres H0 ungueltig.

## Verworfene Vorlaufdiagnosen

Vor der gueltigen Drei-Replik-Serie stoppten zwei Elternaufrufe jeweils vor
Abschluss von R1; R2 und R3 wurden dabei nicht gestartet. Ursache waren
zunaechst eine unvollstaendige 64-Bit-Windows-Handle-Signatur und danach die
falsche Moduladresse `__main__` beim Subprozessstart.

Ein anschliessender einzelner R1-Diagnoseworker bestaetigte die zweite
Ursache. Danach wurde die Prozessadressierung geaendert. Wegen dieses
Quellwechsels gehoeren weder die abgebrochenen Versuche noch der
Diagnoseworker zur gueltigen Kalibrierung. Nur die danach neu gestartete,
quellbitgleiche Serie R1/R2/R3 bildet das gespeicherte Ergebnis.

## Digests und Tests

```text
S1-VY-Vertragsdigest:
ed2872f48ef83b26121bc68ce99ff75462cef9fc60915a7b5b073c45744992cd

S1-VZ-Kalibrierungsdigest:
e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928
```

`10 von 10` neue S1-VZ-Tests pruefen Formeln, Drei-Replik-Zwang,
Plattform-/Quelldrift, Produktionssperre, private API-Grenze sowie die
bitgleiche Rekonstruktion des gespeicherten Ergebnisses. Zusammen mit dem
fokussierten PPB- und Engineeringbestand bestehen `174 von 174` Tests.

## Entscheidung

```text
S1_VZ_PRIVATE_THREE_PROCESS_CALIBRATOR_IMPLEMENTED
S1_VZ_EXACT_THREE_VALID_CLEAN_PROCESS_REPLICATES_ACCEPTED
S1_VZ_PLATFORM_AND_SOURCE_DIGESTS_BIT_EQUAL
S1_VZ_MAX_PEAK_INCREMENT_197292032_BYTES
S1_VZ_MAX_SUCCESS_AND_TEMP_ARTIFACT_34834914_BYTES
S1_VZ_MINIMUM_FREE_MEMORY_2147483648_BYTES
S1_VZ_MINIMUM_FREE_DISK_1073741824_BYTES
S1_VZ_ALL_SAME_VOLUME_ATOMIC_REPLACE_CHECKS_PASS
S1_VZ_CALIBRATION_RESULT_CANONICAL_AND_RECONSTRUCTABLE
S1_VZ_PRODUCTION_EXECUTION_NOT_AUTHORIZED
S1_VZ_ZERO_REGISTERED_MATRIX_PATHS_EXECUTED
S1_VZ_10_OF_10_NEW_TESTS_PASS
S1_VZ_174_OF_174_COMBINED_FOCUSED_TESTS_PASS
```

S1-VZ schliesst die Mess- und Kalibrierungsseite des S1-VX-
Ressourcenblockers. Produktions-Ressourcentyp, H0-Verdrahtung und reale
Autorisierung bleiben noch nicht implementiert.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WA - statischer Produktionsbindungs-, Ressourcen- und
        Autorisierungsvertrag
```

S1-WA darf nur den spaeteren Produktions-Autorisierungstyp, den
Ressourcenbeobachtungs- und Gate-Typ, die Bindung des realen privaten
Producers, den Git-ignorierten Artefaktpfad und die exakte H0-bis-H7-
Verdrahtung festlegen. Noch nicht zulaessig sind Implementierung,
Produktionsentry-Oeffnung, Ressourcen-H0, realer Produceraufruf oder
Matrixausfuehrung.

## Grundlagen

- [S1-VY Ressourcenmess- und Gatevertrag](S1VY_PPB1_STATISCHER_PRODUKTIONS_RESSOURCENMESS_UND_GATEVERTRAG.md)
- [S1-VX Post-Integrations- und Ressourcen-Preflight](S1VX_PPB1_STATISCHER_POST_INTEGRATIONS_UND_RESSOURCEN_PREFLIGHT.md)
- [S1-VW synthetische Einmallaufhuelle](S1VW_PPB1_PRIVATE_SYNTHETISCHE_EINMALLAUF_HANDOFF_UND_TERMINALHUELLEN_ABNAHME.md)
