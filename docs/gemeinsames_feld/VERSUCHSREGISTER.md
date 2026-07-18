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

Der [Technische asynchrone Docknachbarschaftsaudit 015](TECHNISCHER_ASYNCHRONER_DOCKNACHBARSCHAFTSAUDIT_015.md)
trennt lokale Dockfolge und globale Abschlussfolge. Bei kontrollierter
Ratenschiefe bleiben `293/309` auditive, aber `0/15` visuelle Paare global
unmittelbar benachbart; ein Feldschritt je Abschlussgruppe wäre damit erneut
raten- und modalitätsabhängig.

Die [Technische verlustfreie Vorschlagsübergabe 016](TECHNISCHE_VERLUSTFREIE_VORSCHLAGSUEBERGABE_016.md)
ordnet vollständige reduzierte Frames genau einmal zu vorab deklarierten
Vorschlagsspannen. Grobe und feine Segmentierung rekonstruieren dieselben
docklokalen Folgen. Die aktuelle skalare Feldwahrnehmung kann diese variablen
Mengen jedoch noch nicht verlustfrei aufnehmen.

Die [Technische Feldeingangs-Kapazitätsfalsifikation 017](TECHNISCHE_FELDEINGANGS_KAPAZITAETSFALSIFIKATION_017.md)
weist die konkrete Schnittstellengrenze nach: Mehrere Frames desselben Docks
und Kontaktfolgen sind nicht direkt darstellbar, serielle Übergabe bindet den
Feldfortschritt an die Rezeptorrate und reine Endpunkte kollidieren.

Der [Technische Zeitträger-Architekturabgleich 018](TECHNISCHER_ZEITTRAEGER_ARCHITEKTURABGLEICH_018.md)
vergleicht vollständige zeitliche Nutzlast mit serieller lokaler Wirkung. Die
erste bleibt in der Nutzlastgröße, die zweite in der Feldtickzahl
ratenexponiert. Keine Variante wird als Runtime freigegeben.

Der [Funktionale Zeitwirkungsvertrag 019](FUNKTIONALER_ZEITWIRKUNGSVERTRAG_019.md)
registriert zwei unabhängige Anforderungen: gleiche bekannte Kontaktbahn trotz
anderer Segmentdichte muss dieselbe Konsequenz erlauben; unterschiedliche
Kontaktordnung muss dem Kandidaten trotz gleichem Endpunkt und Mittelwert
zugänglich bleiben.

Die [Passive Zeitrepräsentations-Scheiterkarte 020](PASSIVE_ZEITREPRAESENTATIONS_SCHEITERKARTE_020.md)
prüft vier Nullrepräsentationen gegen beide Anforderungen. Segmentanzahl,
Endpunkt und zeitgewichteter Mittelwert tragen nicht beide Achsen. Die
vollständige bekannte Stützbahn trägt sie in den Kontrollen, bleibt aber
variabel breit und ist weder Minimalitätsnachweis noch Runtime-Kandidat.

Die [Passive Kompaktzusammenfassungs-Kollision 021](PASSIVE_KOMPAKTZUSAMMENFASSUNGS_KOLLISION_021.md)
prüft zwei verschiedene, exakt zeitumgekehrte Kontaktbahnen. Dreizehn feste
Lage-, Moment-, Änderungs- und Nachbarschaftskennwerte bleiben vollständig
gleich. Gezeigt ist die fehlende Zeitrichtung dieses Bündels, nicht das
Scheitern jeder kompakten Repräsentation.

Der [Passive gerichtete Zeitmoment-Abgleich 022](PASSIVER_GERICHTETER_ZEITMOMENT_ABGLEICH_022.md)
prüft ein normiertes erstes Zeitmoment. Es bleibt bei bloßer
Segmentverfeinerung gleich und unterscheidet eine Zeitumkehr, lässt aber ein
anderes Paar verschieden geordneter Bahnen kollidieren. Es ist damit eine
gerichtete Projektion, keine eindeutige Zeitkodierung.

Der [Exakte lineare Zeitprojektions-Nullraum 023](EXAKTER_LINEARER_ZEITPROJEKTIONS_NULLRAUM_023.md)
weist mit rationaler Rechnung einen zweidimensionalen Nullraum einer festen
Sechs-Projektions-Bank über acht Kontaktabschnitten nach. Zwei verschiedene
gültige Bahnen kollidieren in Anfang, Ende und den Momenten null bis drei
exakt. Der Befund gilt für feste lineare Banken, nicht für jede Darstellung.

Der Versuch darf nicht:

- Gleichzeitigkeit aus bloß überlappenden Gesamtaufnahmen ableiten,
- eine Beziehung zwischen Docks voraussetzen,
- eine Kopplungs- oder Lernregel ergänzen,
- Semantik, Objekte oder Sprache einführen,
- Aktivität bereits als Feldorganisation interpretieren.
