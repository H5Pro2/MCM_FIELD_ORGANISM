# S2TV-MEDIA-SAMPLING-QUAL-20260919-01

Status: `QUALIFIED` (3/3), genau ein neutraler Aufruf.

| Prüfgruppe | Ergebnis |
| --- | --- |
| Feste Folge und Ressourcen | bestanden: 24 Ereignisse, 20 Formationen, 2 auditive und 2 visuelle Hinweise, 7.392 Feldkontakte, 8 Scans |
| Frame- und Zeitbindung | bestanden: `1/30000`, `30000/1001`, Auswahl `PTS <= Mittelpunkt < nächster PTS`; abweichendes `30/1` abgewiesen |
| Sitzungsschnittstelle | bestanden: `open` → geordnetes `next` → `status` → `stop`; vertauschter Receipt und Neustart abgewiesen |

Der Testaufruf war:

```text
python -B -m unittest tests.test_s2tv_sampled_media_adapter -v
```

Er verwendete nur synthetische PTS-Receipts. Es gab keine Payloadzugriffe,
keine Decoder-, Rezeptor-, NJ-, Feld- oder Memoryausführung und keine
Gateöffnung.

## Verbleibende Anschlussgrenze

Die ausgewählte YouTube-URL ist noch keine technisch gebundene Quelle. Ein
späterer Lauf benötigt einen zulässigen synchronen Zugang zu Audio und Video
mit unveränderlichem Quellenhash. Der Adapter nimmt keine Bildschirm- oder
Audioaufnahme als Ersatz an und wählt weder Frames noch Zeitpunkte anhand von
Inhalt oder Messwerten aus. Die Qualifikation belegt daher nur die
Zeit-/Ereignisform und den Sitzungskontrollpfad, keinen Medien- oder
Memorybefund.
