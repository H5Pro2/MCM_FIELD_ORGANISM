# Versuchsregister des gemeinsamen MCM-Feldes

| Nummer | Status | Forschungsgrenze | Runtimefreigabe |
|---|---|---|---|
| `GF_001` | geschlossen | Gemeinsame Feldtakte und lokale Wirkung aufeinanderfolgender auditiver und visueller Rezeptorzustände im selben Feld | keine |

## Bedeutung des Status

- `geschlossen`: noch keine verbindliche Methodik und kein Lauf,
- `vorregistriert`: Methodik vollständig, aber noch kein Ergebnis,
- `gelaufen`: Messung abgeschlossen, Auswertung noch offen,
- `befundet`: Befund mit begrenzter Evidenzaussage dokumentiert,
- `gestoppt`: Abbruchkriterium erreicht; keine Erweiterung freigegeben.

## Grenze von GF_001

`GF_001` darf erst geöffnet werden, wenn der technische Zeitvertrag einzelne
auditive und visuelle Rezeptorzustände auf derselben Organismusuhr abbildet.

Der [Technische Zeitaudit 001](TECHNISCHER_ZEITAUDIT_001.md) erfüllt den ersten
Teil, zeigt aber null eindeutige 1:1-Zustandspaare. Vor `GF_001` fehlt deshalb
weiterhin ein gemeinsamer Feldtaktvertrag.

Der [Technische Fensteraudit 002](TECHNISCHER_FENSTERAUDIT_002.md) legt reale
Fenster vor den Sensor-Reads fest. In jedem Ein-Sekunden-Fenster treten jedoch
viele auditive und mehrere visuelle native Zustände auf. Damit fehlt weiterhin
eine begründete Trennung zwischen Rezeptorereignis und Feldfortschritt.

Der [Technische Ereigniszeitaudit 003](TECHNISCHER_EREIGNISZEITAUDIT_003.md)
bewahrt alle nativen Zustände, zeigt aber bei einem Ereignis pro möglichem
Feldschritt einen auditiven Anteil von rund 95 %. Vor `GF_001` fehlt deshalb
eine Rateninvarianzprüfung der passiven Feldzeit.

Die [Technische Rateninvarianzprüfung 004](TECHNISCHE_RATENINVARIANZPRUEFUNG_004.md)
zeigt für die bekannte B1-Baseline: Reale verstrichene Dauer beseitigt reine
Segmentratenabhängigkeit, rekonstruiert aber keinen ausgelassenen Kontakt. Vor
`GF_001` fehlt nun ein passiver Zeitspannenvertrag im MCM-Neuronenantrieb.

Der [Technische Zeitspannenvertrag 005](TECHNISCHER_ZEITSPANNENVERTRAG_005.md)
übergibt optional dieselbe gemessene Dauer an alle atomaren
Neuronenvorschläge, ohne Zustand oder Baselines zu verändern. Offen bleibt die
technische Bildung einer lückenlosen Feldzeitfolge aus asynchronen
Rezeptorabschlüssen.

Die [Technische Feldzeitpartition 006](TECHNISCHE_FELDZEITPARTITION_006.md)
deckt drei reale Sekunden lückenlos ab, enthält aber 324 ereignistragende
Grenzen und bleibt damit ratenbestimmt. Offen ist nun die tatsächliche
zeitliche Stütze jedes reduzierten Rezeptorzustands auf der Organismusuhr.

Die [Technische Rezeptorstütze 007](TECHNISCHE_REZEPTORSTUETZE_007.md) trennt
Quellfenster, nominelle Rate und reale Read-Dauer. Audio trägt 100 ms auf der
Sample-Uhr, Video keine belegte Belichtungsdauer; beide bleiben ohne
Weltstützenabbildung auf die Organismusuhr.

Die [Technische Adapterzeitfähigkeit 008](TECHNISCHE_ADAPTERZEITFAEHIGKEIT_008.md)
prüft die tatsächlich gelieferten Backendzeiten in drei realen Läufen.
PortAudio exponiert rückspringende ADC-Zeiten und eine konstante Streamzeit;
DirectShow liefert weder Positionszeit noch PTS oder Belichtungsdauer. Keine
dieser Angaben trägt derzeit eine Abbildung auf die Organismusuhr.

Der [Technische Übergabevertrag 009](TECHNISCHER_UEBERGABEVERTRAG_009.md)
trennt daraufhin unbekannte Außenweltzeit von kausaler Verfügbarkeit im
Organismus. Ein abgeschlossener Rezeptorzustand darf ab seiner gemessenen
Übergabegrenze eintreten; daraus folgen weder Halten noch Wirkungsdauer oder
Feldfortschritt.

Die [Technische Übergabemodell-Falsifikation 010](TECHNISCHE_UEBERGABEMODELL_FALSIFIKATION_010.md)
prüft Punktübergabe, Halten, vollständige Quellfenster und neuen
Quellfortschritt. Keine Variante trägt unter der aktuellen Evidenz einen
gemeinsamen Audio-Video-Eingang ohne Ratenfehler oder zusätzliche Annahme.

Der [Technische Rezeptorzustandsrollen-Abgleich 011](TECHNISCHER_REZEPTORZUSTANDSROLLEN_ABGLEICH_011.md)
weist die tatsächlichen Zustandsbesitzer aus: Audio trägt ein endliches
rollendes Quellenfenster, Video keine Bildgeschichte und der Verteiler nur
Anatomie, aber keine Kontaktgeschichte.

Der [Technische Rezeptorprozessvertrag 012](TECHNISCHER_REZEPTORPROZESSVERTRAG_012.md)
vereinheitlicht daraufhin nur lokale Kausalität, endlichen Zustandsbesitz und
Snapshot-Übergabe. Konkrete Dynamik, Halten, Raten und Modalitätsgewichte
bleiben ausdrücklich offen.

Die [Technische Snapshotänderungs-Falsifikation 013](TECHNISCHE_SNAPSHOTAENDERUNGS_FALSIFIKATION_013.md)
prüft gerichtete und absolute Differenzen. Beide sind gegen identische
Zusatzsnapshots invariant, verlieren jedoch Dauer; ausgelassene Bewegung wird
nicht rekonstruiert.

Der [Technische Neuronenantriebs-Informationsabgleich 014](TECHNISCHER_NEURONENANTRIEBS_INFORMATIONSABGLEICH_014.md)
zeigt, dass vorheriger und aktueller Rezeptorendpunkt sowie Vorschlagszeit
bereits getrennt verfügbar sind. Gleiche Endpunkte und Zeit unterscheiden
aber kontinuierlichen nicht von unterbrochenem Kontakt.

Der Versuch darf nicht:

- Gleichzeitigkeit aus bloß überlappenden Gesamtaufnahmen ableiten,
- eine Beziehung zwischen Docks voraussetzen,
- eine Kopplungs- oder Lernregel ergänzen,
- Semantik, Objekte oder Sprache einführen,
- Aktivität bereits als Feldorganisation interpretieren.
