# Befund: Erhaltung, Verdichtung und Kapazitaetsdruck

## Technischer Abschluss

Der einmalig freigegebene Lauf `retention-capacity-main-20260829-01` wurde
genau einmal ueber `run_main_once` ausgefuehrt und regulaer abgeschlossen.
Der Ausfuehrungsschalter wurde nur fuer diesen Aufruf geoeffnet und danach
wieder auf `False` gesetzt. Der Runner stimmt wieder mit dem versionierten
geschlossenen Stand ueberein.

Der gespeicherte Umfang entspricht vollstaendig der Vorregistrierung:

- 146 Expositionen;
- 170 read-only Inhaltsproben;
- 16 read-only Folgenbefunde;
- 316 Bildanalysen;
- 1296 verkettete Ereignisse;
- Exit-Code 0 und Abschlussmarker `COMPLETE`.

Der danach genau einmal aufgerufene read-only Verifikator meldet
`RECORDING_COMPLETE`, 1296 Ereignisse und keine Beanstandung. Alle 170
Inhaltsproben und 16 Folgenbefunde haben identische Vor- und
Nachzustandsdigests. Die Auswertung wurde anschliessend ausschliesslich aus
den gespeicherten JSON-Belegen berechnet. Es gab keine weiteren Rezeptor-,
Speicher- oder Abrufaufrufe.

## U und V: Wiederholungsabhaengige Verdichtung

In Geschichte U wird N1 zweimal exponiert. Am Checkpoint 2 ist N1 im
TSPM-1-Fast-Bereich abrufbar, aber der Slow-Zustand ist noch nicht stabil.
Nach den Zwischenreizen ist N1 am Checkpoint 6 weder aus Fast noch aus Slow
abrufbar.

In Geschichte V wird N1 viermal exponiert. Dadurch erreicht der visuelle
PPB-1-Prototyp Support 3. Nach dem spaeteren Fast-Verlust ist N1 an den
Checkpoints 7 und 8 weiterhin ausschliesslich aus dem stabilisierten
Slow-Zustand abrufbar.

Damit ist fuer diese gebundenen synthetischen Wahrnehmungswerte die
Gegenueberstellung belegt:

```text
zwei Expositionen  -> kurzfristige Spur -> nach Fast-Verlust nicht abrufbar
vier Expositionen  -> stabiler Slow-Zustand -> nach Fast-Verlust abrufbar
```

## Fast-Ablauf

Geschichte A trennt Ablauf und Slow-Erhaltung. Am Checkpoint 11 ist N1 noch
aus Fast und Slow abrufbar. Schritt 12 weist genau einen abgelaufenen
Fast-Slot aus; danach ist N1 nur noch aus Slow abrufbar und bleibt dies auch
am Checkpoint 13. Der Fast-Verlust ist damit ein protokolliertes Ablaufereignis
nach Nichtverwendung, kein falsch interpretierter Slow-Verlust.

## Slow-Kapazitaetsdruck

In Geschichte C werden N1 bis N4 zuerst mit je vier Expositionen stabilisiert.
Die visuelle Slow-Bank enthaelt danach alle vier stabilen Prototypen. Der
Kapazitaetsdruck fuehrt zu zwei vorab gebundenen Ersetzungen:

- Schritt 18: D1 ersetzt N1;
- Schritt 22: D2 ersetzt N2.

Nach Schritt 18 ist N1 nicht mehr aus Slow abrufbar, N2 bis N4 bleiben
erhalten. Nach Schritt 22 ist auch N2 nicht mehr abrufbar. Am Endcheckpoint 24
sind N3, N4, D1 und D2 aus Slow abrufbar. D1 und D2 wurden jeweils erst nach
weiterer Wiederholung stabil. Die Fast-Ebene und die Slow-Ebene bleiben in
allen Probezeilen getrennt ausgewiesen.

## B4 und Folgenordnung

B4 rekonstruiert in S1 und S2 die gebundene Viererfolge an den Checkpoints 4
und 9 aus den tatsaechlich gespeicherten Bildungsindizes. An den Checkpoints
10 und 11 fehlen nach weiterem FIFO-Druck benoetigte Inhalte; die Reihenfolge
ist deshalb nicht mehr eindeutig verfuegbar.

TSPM-1 meldet an allen acht Folgencheckpoints
`NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE`. Das ist die korrekte technische
Grenze: TSPM-1 erhielt keine neue Reihenfolgekoordinate und nahm nur am
Inhaltsvergleich teil.

## Fehler und Ressourcen

Es gab keine technischen Fehler, keine unvollstaendige Aufzeichnung und keine
read-only Zustandsverletzung. Unter den positiv erkannten Rueckgaben wurde
weder bei B4 noch bei TSPM-1-Fast oder TSPM-1-Slow ein anderes gebundenes
visuelles Muster als das Probeziel ausgewaehlt.

Die gemeinsamen funktionalen Obergrenzen wurden eingehalten. Fuer B4 sind
zusaetzlich 1971 native Schreibwoerter protokolliert. TSPM-1 weist im
Ereignisschema das gebundene funktionale Budget aus; ein davon getrennter
nativer Gesamtkostentraeger ist dort nicht vorhanden und wird deshalb nicht
nachtraeglich konstruiert.

## Einordnung

Der Lauf bestaetigt fuer die sechs begrenzten synthetischen Geschichten eine
technische Zwei-Zeitskalen-Funktion: Wiederholung kann einen stabilen
Slow-Zustand bilden, dieser kann einen Fast-Verlust ueberdauern und wird unter
endlicher Kapazitaet kontrolliert ersetzt. B4 traegt parallel eine begrenzte
explizite FIFO-Reihenfolge.

Das ist ein greifbarer Fortschritt der technischen Memory-Entwicklung. Es ist
kein Nachweis einer allgemeinen oder langfristigen MCM-Memory, keine Semantik,
keine selbststaendige Episodenbildung und keine MCM-Feldwirkung.

## Naechster Schritt

Als naechstes ist eine enge Architekturentscheidung zu treffen: B4 bleibt der
einfache Traeger fuer juengste Inhalte und explizite Kurzfolgen; TSPM-1 bleibt
der Traeger fuer wiederholungsabhaengige Fast-/Slow-Verdichtung. Zu klaeren ist
nur, ob beide Funktionen als getrennte private Bausteine beibehalten werden
oder ob fuer den naechsten begrenzten Wahrnehmungskontext eine gemeinsame
read-only Abfrageschicht erforderlich ist. Eine Feldintegration oder neue
Speichermechanik folgt daraus noch nicht.
