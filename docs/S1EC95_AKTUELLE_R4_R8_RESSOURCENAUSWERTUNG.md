# S1-EC95: Aktuelle r4/r8-Ressourcenauswertung

## Einmaliger Snapshot

Erfasst am `2026-08-13T21:37:00.5368811Z` auf dem aktuellen
Entwicklungsrechner:

- freier physischer Arbeitsspeicher: 5.071.183.872 Bytes
  (ungefaehr 4,72 GiB);
- freier Datentraeger auf `C:`: 234.726.432.768 Bytes
  (ungefaehr 218,61 GiB);
- Ressourcen-Snapshot-Digest:
  `a84308691e4d15bd7b63e69909d54ecdf638fd7394f1b94556c4b8dd82070869`.

Beide Werte liegen zum Erfassungszeitpunkt oberhalb der gebundenen
Mindestgrenzen von 4 GiB beziehungsweise 1 GiB.

## EC94-Auswertung

Die aktuellen EC89-, EC92- und EC93-Objekte wurden zusammen mit dem
Snapshot und einer neuen Nur-Lese-Pruefung der fuenf geschuetzten Artefakte
an EC94 uebergeben.

- alle fuenf Artefakthashes exakt: ja;
- Artefakt-Audit-Digest:
  `af7caaa117dcd876d01b24195b33db47c9bbf7647216b95bb41d95897745d7d7`;
- 14 technische Gates bestanden;
- Besitzerautorisierung vorhanden: nein;
- EC94-Gate-Digest:
  `bc608b5ca68c48757ba99070e0faf763197f970564a181ae1ff7517178a7152c`;
- Entscheidung:
  `TECHNISCH_BEREIT_NEUE_R4_R8_EINMALLAUFFREIGABE_FEHLT`.

## Grenze

Der Snapshot ist zeitpunktbezogen und keine dauerhafte Ressourcengarantie.
EC95 hat keinen Adapter, Wrapper oder Feldkern aufgerufen und keine
Feldschritte ausgefuehrt. Es wurde nichts persistiert, das als Laufresultat
oder Substratbefund gelten koennte. Es besteht kein Memory-, Feldzeit-,
Organisations-, Topologie-, Semantik-, Selbstregulations- oder KI-Nachweis.

Vor einer Ausfuehrung sind zwei Bedingungen zwingend:

1. eine neue ausdrueckliche Besitzerfreigabe fuer genau einen gemeinsam
   gebundenen, nicht persistenten `r4/r8`-Lauf mit maximal 19.248
   Feldschritten;
2. eine unmittelbare Ressourcen-Nachpruefung direkt vor dem ersten
   Adapteraufruf. Faellt sie unter eine Mindestgrenze, ist der Lauf ohne
   Teilstart zu stoppen.

Am besten geht es nach der Besitzerentscheidung mit S1-EC96 weiter: Bei
Freigabe einen verbrauchbaren Exactly-once-Autorisierungsvertrag binden und
unmittelbar vor Ausfuehrung die Ressourcen erneut pruefen. Ohne
ausdrueckliche Freigabe bleibt der reale Pfad geschlossen.
