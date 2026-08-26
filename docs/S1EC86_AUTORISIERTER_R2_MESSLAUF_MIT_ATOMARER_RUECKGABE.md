# S1-EC86: Autorisierter r2-Messlauf mit atomarer Rueckgabe

## Freigabe und Vorpruefung

Der Projekteigentuemer gab genau einen nicht persistenten n2/r2-Messlauf
unter EC83/EC85 mit maximal 3.208 Feldschritten frei. Retry,
Nachparametrierung und eine EC46- oder Forschungsentscheidung waren
ausgeschlossen. Die sechs EC80-Kontraste mussten atomar ueber EC84 gemeinsam
mit dem technischen Ergebnis zurueckgegeben werden.

Unmittelbar vor dem Start wurden im selben Prozess frisch gebunden:

- freier Arbeitsspeicher: `7.118.786.560` Byte;
- freier Datentraeger: `235.023.175.680` Byte;
- EC72-Preflight-Digest:
  `7693d7a11e3c54faaf02185c05e7223e71a09d9f9187f137e891c390a80352fd`;
- EC83-Vertragsdigest:
  `72fc107a4ecd91ff8b8ddf5bb5226990b41c603c81cb763c99ae98d69b92ae88`;
- EC85-Preflight-Digest:
  `10e85930267a744e28e020785b5b866529e75882d79ea1d26b985027bb423cea`;
- EC86-Autorisierungsdigest:
  `59cf46ba1ba458dc0c62257602b4887fd61dab405e5638c5bb9dcc1638e8c001`.

## Messung

Der EC67-Koordinator wurde genau einmal aufgerufen. Der Lauf und die atomare
EC84-Rueckgabe wurden vollstaendig abgeschlossen:

- vier Formationen;
- acht getrennte frische Felder;
- acht Proben;
- 1.608 Bildungs- und 1.600 Probeschritte;
- insgesamt exakt 3.208 Feldschritte;
- Koordinator-Ergebnis-Digest:
  `94d7b93af4a73110526de3f3a9c2481162dacccfceef2dcfc4f703f7012197c5`;
- EC84-Rueckgabe-Digest:
  `dfa323485f111d094e37d6bd579e9477c9c8bdeb29c74bde478693fac3ad7239`;
- EC80-Skalarquittungsdigest:
  `4bad7002743248df059899a65fa9343ffbb16c3bdd0c686c8d4e5cf14053ba59`.

Geordnete `activation`-/`afterimage`-Kontraste:

1. P0-Reset-Ordnung: `0.0` / `0.0`;
2. aktive E1-Ordnung:
   `1.557374244509635e-06` / `9.359585484425281e-07`;
3. Probe-Rueckwirkungsablationsordnung: `0.0` / `0.0`;
4. Bildungsablationsordnung: `0.0` / `0.0`;
5. AB aktiv gegen Probe-Rueckwirkungsablation:
   `2.8709257103076702e-05` / `1.7290444112694203e-05`;
6. BA aktiv gegen Probe-Rueckwirkungsablation:
   `3.0266631347586337e-05` / `1.822640266113673e-05`.

Es erfolgte kein Retry und keine Persistenz von Rohvektoren oder
Skalardateien. Die einmalige EC86-Freigabe ist verbraucht.

## Technische Interpretation

Die gemeinsame P0-Probe zeigt keine AB/BA-Ordnungsdifferenz. Auch nach
Probe-Rueckwirkungsablation und Bildungsablation ist die jeweilige
AB/BA-Ordnungsdifferenz exakt null. Im aktiven E1-Pfad ist dagegen eine
kleine endliche AB/BA-Ordnungsdifferenz in beiden Komponenten messbar.

Der Vergleich aktiv gegen Probe-Rueckwirkungsablation ist fuer AB und BA
ebenfalls endlich und deutlich groesser als die aktive AB/BA-Differenz.
Damit ist auf `r2` technisch eine rollen- und ablationsabhaengige
Probeantwort gemessen. Die atomare Messkette schliesst die in EC78
vorhandene Aufbewahrungsluecke.

## Nichtnachweis

- `r2` ist nur eine Verfeinerungsstufe;
- `r4` und `r8` fehlen;
- numerische Konvergenz und Abstand zum Feinresidual sind ungeprueft;
- EC46 darf nicht entschieden werden;
- keine Aussage zu Robustheit ueber Verfeinerungen oder Wiederholungen;
- kein Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
  Selbstregulations- oder KI-Nachweis.

## Offene Annahmen

Der nicht persistente Lauf liefert eine atomare Skalarquittung, aber keine
Rohvektoren fuer nachtraegliche alternative Auswertungen. Die naechste
wissenschaftlich notwendige Frage ist, ob die aktive Ordnungsdifferenz bei
vorregistriertem `r4/r8` numerisch konvergiert und gegen die Nullkontrollen
stabil bleibt. Schwellen und Regeln duerfen nicht nach diesem Ergebnis
veraendert werden.

Am besten geht es mit S1-EC87 weiter: den EC86-r2-Befund statisch gegen den
vorregistrierten EC46-Vertrag einordnen und einen geschlossenen `r4/r8`-
Ergaenzungsvertrag formulieren. Keine weitere Ausfuehrung ohne neue
ausdrueckliche Freigabe.
