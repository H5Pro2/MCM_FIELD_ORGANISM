# S1-RN: Fokussierter Testlauf und technische Abnahme von Manifestconsumer und Nullfeldfabrik

## Status und Umfang

S1-RN fuehrt ausschliesslich die in S1-RM definierten zehn
Manifestconsumer- und sechs Nullfeldfabriktests aus. Es wurden keine anderen
Tests, keine rollenprivate Fabrik, kein Adapter, keine Matrixzelle und kein
Feldschritt ausgefuehrt.

Abnahmeentscheidung:

```text
SIXTEEN_OF_SIXTEEN_FOCUSED_TESTS_PASSED
S1RK_MANIFEST_CONSUMER_TECHNICALLY_ACCEPTED
COMMON_FOUR_NODE_TICK_ZERO_FIELD_FACTORY_TECHNICALLY_ACCEPTED
PRIVATE_ROLE_FACTORIES_REMAIN_ABSENT
NO_BASELINE_ADVANCE_NO_FIELD_ADVANCE_NO_MATRIX_CELL
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_fresh_*.py" -v
```

Ergebnis:

```text
Ran 16 tests in 0.017s
OK
```

Der Prozess endete mit Exitcode `0`.

## Abgenommene Consumeroberflaeche

Zehn bestandene Tests bestaetigen innerhalb der gebundenen Testoberflaeche:

- das unveraenderte S1-RK-Manifest wird mit seinem registrierten
  Manifestdigest angenommen;
- die geladene Sicht ist rekursiv unveraenderlich;
- Nicht-Bytes, ungueltiges JSON und doppelte JSON-Schluessel werden
  fail-closed abgelehnt;
- unbekannte Rootfelder und abweichende Schemaidentitaeten werden abgelehnt;
- Veraenderungen gemeinsamer und privater Payloads werden ueber ihre Digests
  erkannt;
- Rollenachsen-, Querabhaengigkeits- und Manifestdigestabweichungen werden
  erkannt.

Diese Abnahme gilt genau fuer das registrierte S1-RK-Manifest und den
implementierten Consumer. Sie erlaubt keine automatische Annahme eines neu
berechneten oder erweiterten Manifests.

## Abgenommene Nullfeldoberflaeche

Sechs bestandene Tests bestaetigen innerhalb der gebundenen Testoberflaeche:

- Feld-, Layer-, Geometrie- und Knotenidentitaeten entsprechen dem Manifest;
- die vier Knoten starten mit `S=0.0`, `H=0.0`, Wahrnehmungstakt null,
  Rezeptorkontakt `0.0` und ohne lokale Samples;
- die offene Linie besitzt genau die Kanten a-b, b-c und c-d ohne
  periodische Achse;
- der eine technische Dock bildet vier Carrier verlustlos auf vier Knoten
  ab;
- wiederholte Fabrikaufrufe erzeugen getrennte Feld-, Layer-, Dock-,
  Knoten- und Wahrnehmungsobjekte;
- eine nicht validierte Manifesteingabe wird fail-closed abgelehnt.

Die Fabrik hat in diesem Testlauf kein Feld vorangebracht. Geprueft wurde nur
die Konstruktion des gemeinsamen Zustands bei Takt null.

## Nicht geprueft

S1-RN prueft ausdruecklich nicht:

- die Materialisierung der zwei Zustandslosmarkierungen als Rollenbundle;
- die zwoelf rollenprivaten Frischzustaende;
- die Bruecke zwischen registriertem S1-RK-Kanteninventardigest und nativem
  M-Substrat-Layerdigest;
- private Adapter, Baselinegleichungen oder Carry-Regeln;
- Repliken, Expositionsfolgen, Matrixzellen oder Feldentwicklung;
- eine hypothetische MCM-Memory oder eine andere groessere Faehigkeit.

## Technische Bewertung

Der bisherige Implementierungsweg kann beibehalten werden. Es liegt kein
Befund vor, der eine Aenderung der gemeinsamen Feldarchitektur erfordert.
Der naechste Engpass ist die exakte, rollenweise Uebersetzung der bereits
registrierten privaten Payloads in vorhandene native Wertobjekte, ohne die
beiden unterschiedlichen Kanten-Digestrollen gleichzusetzen.

Diese Uebersetzung ist vor ihrer Implementierung erneut statisch zu binden,
weil B1, B2, B3-B6, A3, M1, M2, M4 und M5 verschiedene native
Zustandsformen besitzen.

## Paketstatus

```text
S1RN_FOCUSED_TECHNICAL_ACCEPTANCE_COMPLETE
MANIFEST_CONSUMER_ACCEPTED
COMMON_PUBLIC_FRESH_FIELD_ACCEPTED
PRIVATE_ROLE_FACTORIES_NOT_IMPLEMENTED
EDGE_DIGEST_BRIDGE_NOT_IMPLEMENTED
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RO - statischer rollenweiser Realisierungs-, nativer Typbindungs- und
        Kanten-Digestbrueckenvertrag fuer die 14 Frischrollen
```

S1-RO muss pro Rolle Quellpayload, Zielwertobjekt, erlaubte Uebersetzung,
Digestpruefung, Objekttrennung und Fail-Closed-Fehler exakt binden. Keine
Implementierung, keine Testausfuehrung, kein Adapteranschluss, keine
Matrixzelle und kein Feldlauf.
