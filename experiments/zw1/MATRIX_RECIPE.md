# ZW1: vor Erzeugung festgelegtes Matrixrezept

2026-10-18, Auftrag 1fd2d773-77de-4aa3-b007-bceafa588386.
Genau eine Matrix, kein wählbarer Seed und keine Auswahl anhand von Ergebnissen.
Namensraum `MCM-ZW1/bootstrap/v1`. Für Zeile r=0…9999 und Spalte c=0…15:
SHA-256 des UTF-8-Texts `MCM-ZW1/bootstrap/v1/row={r}/column={c}`.
Erste acht Digestbytes als vorzeichenlose Big-Endian-Zahl v.
Matrixbyte = `2*(v mod 8) + floor(c/8)`. Modulo 8 ist ohne Rejection unverzerrt.
Jede Zeile enthält acht Paarindizes aus {0,2,…,14} und acht aus {1,3,…,15},
jeweils mit Zurücklegen. Index i bezeichnet das vollständige Paar i+1 mit A/E,
A/F, B/E und B/F. Niemals getrennte Arm- oder Bedingungsindizes.
Dateiformat: 160000 rohe Bytes in Zeilenreihenfolge, keine Header oder Newlines.
Einmalige exklusive Erzeugung; anschließend SHA-256 und unabhängige bytegenaue
Rekonstruktion prüfen. Forschungsquellen bleiben davon getrennt und gesperrt.
