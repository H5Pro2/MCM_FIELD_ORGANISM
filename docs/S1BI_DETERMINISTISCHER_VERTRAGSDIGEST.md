# S1-BI: Deterministischer Vertragsdigest

## Status

Additive technische Driftpruefung. Keine Feldfortschreibung, keine
Persistenz, kein Forschungslauf und kein Memory-, Identitaets-, Substrat-
oder KI-Befund.

## Zweck

`mcm_field_organism.current_api.active_field_state_contract_digest()` liefert
einen stabilen SHA-256-Wert fuer die aktuell importierte maschinenlesbare
Vertragsausgabe aus S1-BH.

Der Digest erlaubt externen Verbrauchern festzustellen, ob sich die
technische API-, Dataclass-, Handoff- oder Snapshotbeschreibung geaendert hat.

## Kanonische Bildung

Die Funktion kodiert `active_field_state_contract()` mit:

```text
UTF-8
sort_keys = true
allow_nan = false
separators = (",", ":")
```

Auf diesen Bytewert wird SHA-256 angewendet. Das Ergebnis ist ein
64-stelliger hexadezimaler Text.

Es werden keine Zeit, kein Zufall, kein Dateipfad, kein Feldsnapshot und kein
Prozesszustand aufgenommen. Gleicher importierter Vertrag erzeugt deshalb im
selben Softwarestand denselben Digest.

## API-Grenze

Der aktive Kern umfasst nun 129 Rollen:

```text
active_field_state_contract
active_field_state_contract_digest
```

sind additive technische Selbstauskunft. Beide Funktionen aktivieren keine
passiven Vergleichs-, C_i-, F3- oder S1B-Pfade.

## Verifikation

Der Test bildet den erwarteten SHA-256-Wert unabhaengig aus der kanonischen
JSON-Ausgabe, vergleicht wiederholte Aufrufe und prueft, dass eine lokale
Mutation des zurueckgegebenen Dictionaries keinen spaeteren Vertrag aendert.

## Aussagegrenze

Der Digest ist kein Feldinhalt, keine Organismusidentitaet, kein Gedaechtnis
und kein Nachweis von Selbstwahrnehmung. Er ist ausschliesslich ein technischer
Fingerabdruck der aktuellen Schnittstellenbeschreibung.

## Bester naechster Schritt

Der externe Zustandsvertrag ist damit maschinenlesbar und driftpruefbar.
Weitere Metadatenfunktionen sind aktuell nicht erforderlich. Der
anschliessende Abschlussaudit S1-BJ findet keine offene technische Luecke in
der aktiven AV-Engineeringstrecke.
