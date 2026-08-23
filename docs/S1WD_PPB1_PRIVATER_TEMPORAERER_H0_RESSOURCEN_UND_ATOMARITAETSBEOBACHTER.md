# S1-WD: Privater temporaerer PPB-1-H0-Ressourcenbeobachter

## Auftrag und Grenze

S1-WD implementiert den ersten realen H0-Ressourcenbeobachter. Seine reale
Wirkung bleibt auf Betriebssystemabfragen und genau eine Atomaritaetsprobe in
einem dedizierten temporaeren Testverzeichnis begrenzt.

Nicht Bestandteil sind:

- Produktionsautorisierung;
- Produktions-Lock oder terminales Produktionsartefakt;
- realer Producer, Pipeline- oder Matrixaufruf;
- Produktions-, Feld- oder Medienpfad;
- oeffentliche API oder Snapshotaenderung.

## Beobachtete Rollen

Der Beobachter liefert an den vorhandenen privaten S1-WB-Typ:

- aktuell verfuegbaren physischen Speicher;
- aktuell freien Platz auf dem Testvolume;
- aktuelle Plattformbindung;
- Digests der vier kalibrierten S1-VQ-, S1-VT-, S1-VW- und S1-VZ-Quellen;
- Volumeidentitaet fuer Testartefakt und Temporaerpfad;
- Same-Volume-Ergebnis;
- Ergebnis einer atomaren Replace-Probe;
- Freiheit der hypothetischen Lock-, Erfolgs-, Fehler- und Temporaerpfade.

Die Ressourcenwerte sind fluechtig. Sie werden bei jedem Aufruf neu gelesen
und nicht als dauerhaftes Ergebnis oder Freigabe gespeichert. Die gebundenen
Untergrenzen bleiben `2 GiB` freier physischer Speicher und `1 GiB` freier
Datentraegerplatz.

## Dateisystemgrenze

Akzeptiert wird nur ein existierendes Verzeichnis namens
`s1wd-h0-observer` unter der vom Betriebssystem gemeldeten
Temporaerwurzel. Insbesondere werden abgelehnt:

- ein gleichnamiges Verzeichnis im Projektarbeitsbereich;
- ein abweichend benanntes Temporaerverzeichnis;
- die PPB-1-Produktionswurzel und ihre Unterverzeichnisse;
- ungueltige oder nicht synthetisch markierte Ausfuehrungs-IDs.

Die Atomaritaetsprobe schreibt einen neuen Temporaerpfad, synchronisiert ihn,
ersetzt ihn mit `os.replace`, prueft den unveraenderten Inhalt und entfernt
beide Proberollen. Bereits belegte Probewege werden nicht ueberschrieben,
sondern fuehren zum Fail-Closed-Ergebnis.

## Abnahme

Die elf neuen Tests bestaetigen:

- reale positive Speicher- und Datentraegerbeobachtung;
- aktuelle Plattform- und Quellbindung;
- Auswertung durch das bestehende S1-WB-Ressourcengate;
- genau eine rueckstandsfreie Atomaritaetsprobe;
- getrennte Erkennung belegter hypothetischer Artefaktpfade;
- Fail-Closed ohne Ueberschreiben eines belegten Probewegs;
- Ablehnung falscher Temporaer-, Workspace- und Produktionswurzeln;
- Ablehnung ungueltiger Ausfuehrungs-IDs vor jeder Probe;
- weiterhin gesperrten Produktionsentry;
- null Runner-, Pipeline- und Kalibrierungsaufrufe;
- private API- und Snapshotneutralitaet.

Ergebnis:

```text
S1_WD_REAL_OS_RESOURCE_OBSERVATION_ACCEPTED_FOR_TEMPORARY_TEST_ROOT_ONLY
S1_WD_SAME_VOLUME_AND_SINGLE_ATOMIC_REPLACE_PROBE_ACCEPTED
S1_WD_PROBE_CLEANUP_AND_EXISTING_PATH_FAIL_CLOSED_ACCEPTED
S1_WD_PRODUCTION_ROOT_AUTHORIZATION_PRODUCER_AND_ENTRY_BLOCKED
S1_WD_ZERO_PRODUCTION_ARTIFACTS_AND_MATRIX_CALLS
S1_WD_11_OF_11_NEW_TESTS_PASS
S1_WD_191_OF_191_CURRENT_FOCUSED_PPB1_TESTS_PASS
```

Eine kontrollierte Einzelbeobachtung waehrend der Abnahme bestand alle
vorhandenen Ressourcengates und hinterliess ein leeres Testverzeichnis. Ihre
momentanen Speicherwerte und Digests sind keine Autorisierung und werden
nicht als stabile Vertragswerte verwendet.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-WE - private Lock- und Terminaltypen mit synthetischer
        Temporaerdateisystemabnahme
```

S1-WE darf ausschliesslich die dauerhafte Einmallaufmarkierung sowie
wechselseitig ausschliessende Erfolgs- und Fehlerrollen als private Typen
implementieren und im Temporaerdateisystem pruefen. Autorisierung,
Producerbindung, Produktionspfad, reale Matrix und Feldpfade bleiben
gesperrt.

## Grundlagen

- [S1-WC statischer Post-Implementierungs-Preflight](S1WC_PPB1_STATISCHER_POST_IMPLEMENTIERUNGS_PREFLIGHT_DER_PRODUKTIONSROLLEN.md)
- [S1-WB private Produktionsrollen und synthetische H0-Abnahme](S1WB_PPB1_PRIVATE_PRODUKTIONSROLLEN_UND_SYNTHETISCHE_H0_GATEABNAHME.md)
- [S1-WA Produktionsbindungs- und Autorisierungsvertrag](S1WA_PPB1_STATISCHER_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_AUTORISIERUNGSVERTRAG.md)
