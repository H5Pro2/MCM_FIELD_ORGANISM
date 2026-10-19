# S2TV: Gebundene Medienzeit- und Auswahlanschluss

Auftragskennung: `S2TV-MEDIA-SAMPLING-20260919-A`.

Dieser private Anschluss verarbeitet noch keine Medienpayloads, Rezeptoren,
Feld- oder Memoryzustände. Er bindet ausschließlich die Auswahlreihenfolge
und die Zeitformen für einen später separat freizugebenden Versuch mit dem
vom Benutzer ausgewählten Video.

## Feste Folge

Jeder Durchlauf verwendet zehn 100-ms-Audiofenster bei Medienzeit `0,0`,
`0,5`, ..., `4,5` Sekunden. Für jedes Fenster bindet der Adapter den letzten
Videoframe mit `PTS <= Fenstermittelpunkt` und den nächsten Frame mit
`PTS > Fenstermittelpunkt`. Auswahlzeit, tatsächlicher Frame-PTS, Zeitbasis
und Runtimezeit stehen getrennt im Receipt.

Es gibt zwei Durchläufe. Die Medienzeit des zweiten beginnt wieder bei null;
die Runtimezeit bleibt streng steigend. Bei Medienzeit `1,0` und `4,0`
erfolgen im zweiten Durchlauf je ein auditiver und ein visueller read-only
Hinweis vor der dortigen Formation.

| Größe | Wert |
| --- | ---: |
| Ereignisse | 24 |
| Formationen | 20 |
| auditive / visuelle Hinweise | 2 / 2 |
| Audioanalysen / NJ-Projektionen | 22 / 22 |
| visuelle Analysen | 22 |
| Feldkontakte | 7.392 |
| Scanbelege | 8 |

Damit passt die Folge in die bestehenden Grenzen von 28 Ereignissen,
20 Formationen, zwei auditiven und sechs visuellen Hinweisen. Decoderarbeit
und später tatsächlich an MCM übergebene Ausschnitte bleiben getrennt zu
zählen.

## Zeitprofil und Grenzen

Das native Videoprofil ist unverändert `30000/1001` fps bei Zeitbasis
`1/30000`; es wird nicht als native 30 fps ausgegeben. Audio verwendet
`1/48000`. Der Adapter akzeptiert weder abweichende Zeitbasen noch eine
Frameauswahl außerhalb des gebundenen PTS-Intervalls.

Die aktuelle YouTube-URL ist nur die Quellenwahl. Für einen realen Lauf fehlt
noch eine zulässige, bytegebundene lokale oder ausdrücklich unterstützte
Medienquelle mit Hash sowie ein synchroner Decoderzugang für Audio und Video.
Der Adapter wechselt nicht selbständig zur Bildschirm- oder Audioaufnahme.

Die neutrale Qualifikation prüft ausschließlich Auswahl, PTS-Bindung,
zweiten Durchlauf, begrenzten Sitzungszustand und kontrollierten Stopp. Sie
qualifiziert weder den ausgewählten Videoinhalt noch Speicherbildung oder
Abruf.
