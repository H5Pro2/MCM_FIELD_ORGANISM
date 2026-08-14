# S1-EA3: E1 kanonischer Release-Preflight

## Status

Der private statische Release-Preflight bindet den S1-EA2-Gesamtproduzenten,
den vorhandenen S1-DX-Exactly-once-Kern, den S1-DW-Berichtsvertrag und alle
drei freien S1-EA-Zielpfade. Er fuehrt weder Produzent noch Executor aus.

Eine Ausfuehrungsfreigabe ist weiterhin unzulaessig: Der gebundene
S1-DX-Executor ist absichtlich synthetisch und verweigert den kanonischen
Projektordner. Ein kanonischer Executoradapter existiert noch nicht.

## Implementierung

```text
mcm_field_organism/e1_canonical_refined_chain_release_preflight.py
tests/test_e1_canonical_refined_chain_release_preflight.py
```

Normalisierter Implementierungsdigest:

```text
5041990a4c8598894d9674fc8277e6574eec94898dcfa5ec29985ac1c196c0c2
```

## Gebundene Oberflaechen

Der Preflight prueft wiederholbar:

- den aktuellen S1-DW-Einmallaufvertrag;
- den aktuellen S1-DY-Bindungsdigest;
- den kanonischen JSON-Digest der S1-EA2-Verdrahtung;
- den normalisierten S1-EA2-Implementierungsdigest;
- den unveraenderten S1-DX-Executor-Kerndigest;
- die vollstaendige S1-DW-Berichtsfeldreihenfolge;
- Ergebnis-, Versuchs- und Sperrpfad als drei freie Geschwister;
- den unveraenderten S1-DN-Upstreambericht.

Der Produzent und der Executor-Kern gelten als gebunden. Der kanonische
Executor bleibt explizit ungebunden. Ausfuehrung, Persistenz, automatischer
Retry und starke Aussagen bleiben falsch.

## Fail-closed-Regeln

- Veraenderte Implementierungsdigests stoppen den Preflight.
- Ein bereits verwendeter Zielpfad stoppt vor jeder Ausfuehrung.
- Jede manuelle Aktivierung eines Release-Flags wird vom Dataclass-Vertrag
  abgewiesen.
- Preflight-Wiederholungen schreiben keine Datei.
- Produzenten- und Executoraufrufe kommen im Preflight nicht vor.

## Technische Abnahme

```text
5 fokussierte Tests
391 Tests im vollstaendigen E1-Verbund
OK
```

Die S1-EA-Zielpfade sind weiterhin frei. Der S1-DN-Bericht hat weiterhin den
SHA-256-Digest
`cddcf121cf2fcca7145f406157cfff49c91cff526db8937520ae1c7705431ef9`.

## Aussagegrenze

S1-EA3 erzeugt keine Messwerte und begruendet keinen Bildungs-, Transfer-,
Memory-, Semantik-, Organisations-, Topologie-, Selbstregulations- oder
KI-Befund.

## Anschluss

S1-EA4 implementiert nun den kanonischen Executoradapter und nimmt dessen
Exactly-once-Politik ausschliesslich an temporaeren Spiegelpfaden ab. Der
produktive Einstieg bleibt bis zum letzten Freigabegate gesperrt.
