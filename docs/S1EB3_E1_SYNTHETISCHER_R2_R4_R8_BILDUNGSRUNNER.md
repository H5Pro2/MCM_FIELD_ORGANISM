# S1-EB3: Synthetischer E1-r2/r4/r8-Bildungsrunner

## Status

Der private S1-EB-Bildungsrunner ist fuer `r2/r4/r8` implementiert und nur
mit einer kleinen synthetischen AB-/BA-Quelle abgenommen. Die kanonische
Quelle wird vor jeder Runtimeausfuehrung abgewiesen. Es wurde keine Probe
ausgefuehrt und kein Einmallaufpfad angelegt.

## Implementierung

```text
mcm_field_organism/e1_confirmation_formation_runner.py
tests/test_e1_confirmation_formation_runner.py
```

Normalisierter Implementierungsdigest:

```text
7b4fe5870bf8476b1e0367a6f8a7ad52ff026065d9945144aa3f27339663febd
```

## Runnergrenze

Der Runner verwendet unveraendert die bestehende E1- und neutrale
asynchrone Feldruntime. Sein eigenes Ergebnisformat ist streng auf
`r2/r4/r8` begrenzt und enthaelt je Verfeinerung:

```text
AB aktiv
BA aktiv
AB Identitaetswiederholung
AB Bildungsablation
BA Bildungsablation
```

Alle Arme beginnen mit objektgetrennten Kopien desselben frischen Feldes
und desselben neutralen E1-Zustands. Die Feldrueckwirkung bleibt waehrend
der Bildung ausgeschaltet. Supports werden genau einmal zugeordnet und die
lokale Ressourcenbilanz wird mit einem Fehlerboden von `1e-12` kontrolliert.

## Synthetische Abnahme

- `r2`, `r4` und `r8` wurden vollstaendig verbraucht.
- Die AB-Identitaetswiederholung ist zustandsidentisch und objektgetrennt.
- Beide Bildungsablationsarme bleiben exakt neutral.
- Aktiver und ablatierter Feldpfad bleiben bei ausgeschalteter
  Rueckwirkung exakt gleich.
- Vertauschte AB-/BA-Planmengen werden vor Ausfuehrung abgewiesen.
- Eingabefeld und Eingabezustand bleiben unveraendert.
- Wiederholung erzeugt denselben synthetischen Produktionsdigest.

```text
Produktion 2a9190cbdc53a974e20d78295dfa8b97ebf979ed56454256ad9c70998747c5fc
r2         35d49de570ebebec05eba5626592393bef333f2cdd3317696abefc1a5a51ecc5
r4         a4ebda876d32952040cef7c3f154b3148a217c587dc786bc168bf6e1c53b3cfe
r8         3cf6b073349bc464c29c7b33edd80f4485f0af60e1e7bc7375e4e79d65c39c78
```

Diese Digests binden nur die synthetische Testfixture und sind kein
Forschungsbefund.

## Technische Abnahme

```text
9 fokussierte S1-EB3-Tests
439 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-EB3 zeigt nur, dass die bestehende Bildungsmechanik die neuen
`r2/r4/r8`-Plaene technisch kontrolliert verarbeiten kann. Es wurde nicht
ermittelt, ob kanonische AB-/BA-Zustaende verschieden sind. Es folgt kein
Memory-, Semantik-, Organisations-, Topologie-, Selbstregulations- oder
KI-Befund.

## Anschluss

S1-EB4 hat den spaeteren Bestaetigungslauf statisch an S1-EB bis S1-EB3,
die unveraenderte Transfer- und Probemechanik, die kanonischen Quellen, alle
Pflichtkontrollen und die vorregistrierte Entscheidung gebunden. Es wurde
nichts kanonisch ausgefuehrt. Siehe
[S1-EB4 statischer Bestaetigungskettenvertrag](S1EB4_E1_STATISCHER_BESTAETIGUNGSKETTENVERTRAG.md).
