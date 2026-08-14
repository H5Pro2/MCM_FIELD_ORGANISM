# W7-AV: Roher Observer-Siebenpfad-Kontrastbinder

## Entscheidung

`OBSERVER_SEVEN_PATH_RAW_CONTRASTS_BOUND`

W7-AV bindet die bereits in W7-AC materialisierten LEAK-, SAT- und
NORM-Ergebnisse additiv an eine endliche rohe Vergleichsoberflaeche. Es wird
keine Feldintegration erneut ausgefuehrt und kein Forschungsreport erzeugt.

## Methodische Korrektur

Der W7-AT-Effektboden stammt aus R1/R2/R4-Abstaenden der S/H-Feldmessflaeche.
Observerausgaben liegen auf der getrennten Messflaeche E. Der Feldboden wird
daher nur als Provenienz gebunden und ausdruecklich nicht auf Observerwerte
angewendet. Dies folgt direkt aus W7-O: Feldmodelle verwenden den
Verfeinerungsboden, lokale Observerkerne dagegen ihre exakte
Segmentfortschreibung.

## Implementierung

`mcm_field_organism/w7av_observer_path_contrast_binder.py` bildet fuer jedes
der drei Modelle acht vorregistrierte Pfadvergleiche:

- AB gegen UB und AG gegen UG fuer alte A-Wirkung;
- AB gegen AG und UB gegen UG fuer neue B-Wirkung;
- BA gegen UA und BG gegen UG fuer alte B-Wirkung;
- BA gegen BG und UA gegen UG fuer neue A-Wirkung.

Jeder Vergleich enthaelt genau fuenf rohe, nichtnegative
`observer_output_trace_linf`-Abstaende. Insgesamt entstehen 24 Kurven mit 120
Checkpointwerten. Die Probezeit- und Geometrieachsen muessen paarweise exakt
uebereinstimmen; andernfalls stoppt der Binder.

## Gesperrte Ableitungen

W7-AV normalisiert keine Kurve und waehlt keine Observererklaerung. Es
entscheidet weder Feldfunktion noch Memory. LEAK, SAT und NORM bleiben externe
Erklaerungsmodelle ohne Feedback, Persistenz, M oder Ressourcenrolle.

## Naechster Schritt

W7-AW muss statisch einen Observer-eigenen Aufloesungs- und Profilvergleich
definieren. Er darf den W7-AT-Feldboden nicht wiederverwenden und muss vor
einer LEAK-/SAT-/NORM-Erklaerungsentscheidung eine dimensionslose,
vorregistrierte Vergleichstoleranz festlegen.
