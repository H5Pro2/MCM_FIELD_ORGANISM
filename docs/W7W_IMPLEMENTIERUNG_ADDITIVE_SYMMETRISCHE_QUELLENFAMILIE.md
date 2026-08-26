# W7-W: Implementierung der additiven symmetrischen Quellenfamilie

## Entscheidung

`ADDITIVE_SYMMETRIC_SOURCE_FAMILY_IMPLEMENTED`

W7-W implementiert den statischen W7-V-Vertrag. Es wurden nur neue
kontrollierte Quellenobjekte, technische Supportpruefungen, Digests und eine
optionale W7-R-Autorisierung erzeugt. Eine Pfadmatrix oder ein Forschungsrun
wurde nicht gestartet.

## 1. Implementierte Rollen

Das isolierte Modul
`mcm_field_organism/w7w_symmetric_source_family.py` erzeugt:

- vier B-Praefixschritte auf 0 bis 4;
- einen verlustfrei kombinierten B-Praefix;
- vier A-Fortsetzungsschritte auf 4 bis 8;
- den Digest des unveraenderten K2-B-Basisinventars;
- einen symmetrischen Inventardigest;
- die vollstaendige Quellenbelegung fuer AB, AG, BA, BG, UA, UB und UG;
- neun explizite Autorisierungsrollen fuer W7-R.

Die beiden additiven Rollen werden frisch aus `changed.phases[2]` und
`same.phases[0]` reduziert. `_phase_steps` besitzt dafuer eine optionale
Snapshot-Namespace. Ohne diese Option bleibt sein bisheriges Verhalten
unveraendert. W7-W verwendet die vertraglichen Welt-IDs als Namespace, weil
die zugrunde liegende Reduktionspipeline Snapshot-IDs sonst nur aus
Modalitaet und Cursor bildet.

## 2. Technische Supportabnahme

Praefix- und Fortsetzungssupport bestehen. Verglichen werden ausschliesslich:

- Modalitaet und Geometrie;
- Uhr und Carrierinventar;
- Framezahl;
- absolute Intervallgrenzen beim Praefix;
- relative Abschlussgrenzen je Fortsetzungsschritt.

Rezeptorwerte werden weder verglichen, normalisiert noch angeglichen. Die
vorhandene A-Quelle und die neue B-Quelle behalten verschiedene Digests und
Snapshot-Identitaeten.

## 3. Gebundene Digests

```text
B-Praefixschritte:
09b11485f0d176ffdd9a08b0ac64b7302cbe93a1707a3f10f597f89319151f90
8f5b821492293755285400e834705e0ba27453ab2f4754c412ebb5181c8146d9
59ad3054225b7ecf46dd786f46f089c22fba05960ad0e6c283fd22e5e89682e4
618788be2e790f117d0f4cbec110254127dde46c9010c74879fc8f4c75f4fa79

kombinierter B-Praefix:
e86f3ba45065e1d91aaa6c197f5b2b64c814260fbfe2bcd0f75218307f1502c4

A-Fortsetzungsschritte:
b294d666d6ea17f27f1d237bf175aaa6c0df745b626e681f49452f4f4a3e8455
56e43079eb0f8b4e8b3cab06acadbe310a75715822aa36d1cc58a556190effa4
204dbd043c14c53a8690a3b06ee2f5d50617ada1e5d95194dd7e3f4f0ebef6b6
93639b02b225f7a365b0dec59cfd6c67d8cd3a931d96956951ef30ee7444d374

symmetrisches Inventar:
de1504db9b1882abf38ad53919be2f5500ccf339f41ce91cb69f3e44a121605e

Autorisierung:
946f719f11f240bc57052a48ed177ce88d52fc0d86ee18d97aef7d92bccf07b5
```

## 4. W7-R-Grenze

`produce_w7r_p0_s_completion_states` besitzt nun den optionalen Parameter
`source_authorization`. Ohne ihn akzeptiert W7-R weiterhin nur das
vorhandene W7-M-Quelleninventar. Eine additive Quelle wird nur angenommen,
wenn gemeinsam passen:

- W7-M-Matrixdigest;
- Basisinventardigest;
- symmetrischer Inventardigest;
- Quelldigest;
- technische Quellenrolle;
- erlaubter Pfad;
- exaktes Intervall;
- Digest der tatsaechlich uebergebenen Sequenzen.

W7-W wird weder aus dem Paketwurzelmodul noch aus `current_api` exportiert.

## 5. Verifikation

Die neue Testsuite enthaelt 12 Tests. Zusammen mit den direkt betroffenen
K2-B-, W7-M- und W7-R-Tests bestehen 33 Tests. Der breitere W7-Verbund
besteht mit:

```text
Ran 60 tests
OK
```

Geprueft wurden unter anderem deterministischer Wiederaufbau, exakte
Intervalle, verlustfreie Kombination, technische Supportgleichheit,
unveraenderte Matrix- und Regionsdigests, sieben eindeutige Pfade sowie die
Ablehnung fehlender, falscher oder manipulierter Autorisierungen.

## 6. Aussagegrenze

W7-W weist nur die technische Vollstaendigkeit der Quellenfamilie und ihrer
Zulassung nach. Es wurde keine Pfadmatrix ausgefuehrt und kein Modellzustand
verglichen. Daraus folgen keine Feldfunktion, kein Memory, keine Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## 7. Naechster Schritt

W7-X soll statisch einen siebenpfadigen Quellplan binden. Er muss Segment-
und Checkpointreihenfolge, Zustandkopien und Digestfortsetzung festlegen,
ohne eine Matrix, ein Modell, einen Browser, Report oder Forschungslauf zu
starten.
