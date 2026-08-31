# S2-HJ-Neuqualifikation: statischer Vorbedingungsaudit

Status: `S2HJ_REQUALIFICATION_BLOCKED_FIXTURE_SCOPE_INCOMPLETE`

## Auftrag und Grenze

Vor einem neuen Qualifikationslauf wurde rein statisch geprueft:

- kanonische Herkunft, Zeichenform und maximale Laenge der Run-Owner-ID;
- Ableitbarkeit der neutralen Owner-ID aus der vorgesehenen Planbindung;
- Materialisierbarkeit aller 60 Projektionen bei maximal gueltiger Owner-ID;
- Einhaltung der Grenze, ausschliesslich die neutrale Fixture-ID zu korrigieren.

Es wurde kein Test aufgerufen, kein Projektmodul ausgefuehrt und keine Datei des
Produktions-, Projektions- oder Testcodes geaendert. Der Kontextfunktionslauf
bleibt gesperrt.

## Owner-ID-Vertrag

Die verbindliche Zeichen- und Laengengrenze existiert bereits in
`tools/_s2gt_private_append_only_recorder.py`:

```text
^[a-z][a-z0-9-]{7,95}$
```

Damit gelten:

- ausschliesslich kleingeschriebene ASCII-Buchstaben, Ziffern und Bindestriche;
- erster Buchstabe zwingend `a-z`;
- minimale Laenge 8 Zeichen;
- maximale Laenge 96 Zeichen.

`ExecutionPlan.build` ist die kanonische Abnahmegrenze. Der Owner wird dem Plan
aus der vorab autorisierten Run-Bindung uebergeben und dort gemeinsam mit der
Run-ID validiert. S2-GR bindet seine Herkunft an die vorab autorisierte Run-ID
und Run-Autorisierung; Bild, History, Fall, Zielwert und Ergebnis sind als
Quellen ausgeschlossen.

S2-HE und der bestandene S2-HF-Wiederholungsaudit berechnen alle kompakten
Huellen bereits mit einer maximal 96 Zeichen langen Owner-ID. Eine neue
Laengengrenze ist daher nicht erforderlich.

## Korrektur der bisherigen Diagnose

Die fehlgeschlagene S2-HJ-Fixture verwendete:

```text
s2hj-neutral-owner- + 72 * x
```

Ihre Laenge betraegt 91 Zeichen. Sie ist damit nach dem bestehenden Vertrag
gueltig und nicht ueberlang. Die bisherige Formulierung, die ID sei kuenstlich
ueberlang beziehungsweise bereits selbst ungueltig, war nicht korrekt.

Der tatsaechliche zweite Fixtureunterschied liegt in der S2-GC-Sequenzform:

- gebundener S2-GT-Lauf: `NOT_REQUESTED` und keine Sequenzreferenz;
- neutrale S2-HJ-Fixture: `AVAILABLE` und genau eine 64-stellige
  Sequenzreferenz.

Der produktive Runner bindet fuer die vier S2-GC-Projektionen ausdruecklich
`ValidatedB4ShortSequenceEvidence.build("NOT_REQUESTED", ...)`. Der S2-HF-
Wiederholungsaudit weist fuer die stabile S2-GC-Vollform bei maximaler
96-Zeichen-Owner-ID exakt 3.174 Byte aus.

Die abweichende neutrale Sequenzform vergroessert die kanonische Huelle netto
um 62 Byte:

```text
eine Digestreferenz in []: +66 Byte
AVAILABLE statt NOT_REQUESTED: -4 Byte
Netto: +62 Byte
```

Damit ergibt sich statisch:

```text
gebundene Vollform bei 96-Zeichen-Owner: 3.174 Byte
abweichende neutrale Sequenzfixture:       +62 Byte
neue Fixture bei maximalem Owner:        3.236 Byte
```

Das ueberschreitet sowohl die Rollenobergrenze von 3.174 Byte als auch die
allgemeine Kompaktprojektionsgrenze von 3.200 Byte. Eine ausschliessliche
Aenderung der Owner-ID kann diesen Widerspruch bei maximal gueltiger Laenge
nicht schliessen.

## Herkunftsgrenze der aktuellen Testfixture

Die aktuelle neutrale Testfixture erzeugt ausserdem nur ein
`SimpleNamespace`-Planfragment. Dadurch wird die Owner-ID nicht durch
`ExecutionPlan.build` abgenommen. Eine andere Zeichenfolge allein wuerde die
geforderte kanonische Planherkunft daher nicht vollstaendig nachweisen.

Eine gueltige Neuqualifikation muss einen realen, rein technischen
`ExecutionPlan` fuer die neutrale Huelle verwenden oder einen daraus
unveraendert uebernommenen Planbeleg binden. Das ist eine Fixturekorrektur,
keine Produktionscodeaenderung.

## Entscheidung

Die bedingte Freigabe erlaubt ausschliesslich die Korrektur der neutralen
Fixture-ID. Das reicht statisch nicht aus:

1. Die alte ID war bereits formell gueltig.
2. Die Sequenzfixture weicht vom gebundenen Laufplan ab und ueberschreitet bei
   maximal gueltigem Owner die Groessengrenzen.
3. Die aktuelle Fixture umgeht die kanonische `ExecutionPlan.build`-Abnahme.

Deshalb wurde kein neuer `unittest`-Aufruf gestartet.

Status:

`S2HJ_REQUALIFICATION_BLOCKED_FIXTURE_SCOPE_INCOMPLETE`

Fuer den naechsten Schritt ist eine ausdruecklich erweiterte, weiterhin enge
Fixturefreigabe erforderlich. Sie muss genau zwei Korrekturen zulassen:

- Ownerbindung ueber einen gueltigen `ExecutionPlan` mit einer 96 Zeichen
  langen, vertraglich abgenommenen neutralen Owner-ID;
- neutrale S2-GC-Sequenzevidenz exakt wie im gebundenen Laufplan als
  `NOT_REQUESTED` ohne Referenzen.

Produktionscode, Projektionen, Validatoren und die zwoelf Testziele koennen
dabei unveraendert bleiben. Erst danach ist genau ein neuer Qualifikationslauf
unter neuer ID methodisch zulaessig.
