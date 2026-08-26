# S1-HD: Lauf 197 technischer Vorstartabbruch

Stand: 2026-08-15

Status: `TECHNICAL_PRESTART_IMPORT_ABORT_NO_FIELD_STEPS`

## Beobachtung

Der vorregistrierte Lauf-197-Einstieg wurde genau einmal mit direktem
Dateipfad gestartet. Python setzte dabei das Werkzeugverzeichnis statt der
Projektwurzel an den Anfang des Modulpfads. Der Import der lokalen
Fixturequelle brach deshalb unmittelbar ab:

```text
ModuleNotFoundError: No module named 'tests'
```

Der Fehler trat vor Konstruktion der S1-GK-Quelle und vor der einzigen
S1-GU-Aufrufstelle auf.

```text
S1-GU-Aufrufe:                  0
verarbeitete Arme:              0
Transitionen:                   0
reale Feldschritte:             0
Supports:                       0
atomare Ergebnisrueckgabe:      nein
Persistenz:                     nein
Retry:                          nein
```

## Technische Interpretation

Die Ursache liegt ausschliesslich in der Startform des Python-Werkzeugs. Ein
reiner Import ueber den Projektwurzel-Modulpfad bestand anschließend, ohne
`main()` oder S1-GU aufzurufen. Der Lauf-197-Einstieg ist nach dem Abbruch
dauerhaft mit `EXECUTION_PERMITTED = False` versiegelt und kann nicht als
Retry verwendet werden.

## Evidenzgrenze

Es existiert kein Fixed-Adapter-Messergebnis aus Lauf 197. Der Abbruch sagt
nichts ueber Feldwirkung, AB/BA-Unterschiede, E1, Memory oder andere
Forschungsfragen aus. Die Einmallauffreigabe ist verbraucht.

## Naechster Schritt

Vor einer neuen Ausfuehrung muss ein neuer, vom Projektwurzel-Modulstart
abgenommener Einstieg mit neuer Laufnummer vorbereitet werden. Danach ist
eine neue ausdrueckliche Einmallauffreigabe erforderlich.
