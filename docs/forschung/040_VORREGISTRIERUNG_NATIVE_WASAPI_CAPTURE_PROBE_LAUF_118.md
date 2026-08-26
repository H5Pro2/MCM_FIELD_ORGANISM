# Forschung 040: Vorregistrierung nativer WASAPI-Capture-Probe

## Lauf und Status

```text
Lauf:                    118
Dokumentart:                      technische Vorregistrierung
Native Probe implementiert:       nein
Hardwarelauf durchgefuehrt:       nein
Rezeptor- oder Feldanbindung:     gesperrt
Quellenstuetze nachgewiesen:      nein
```

Dieses Dokument spezifiziert ausschliesslich den Implementierungs- und
Abbruchvertrag fuer einen spaeteren, gesondert freizugebenden nativen
WASAPI-Capture-Probe. Es erweitert weder Produktcode noch Audioadapter und
startet keine Hardware-, Rezeptor-, Kamera- oder Feldruntime.

## Forschungsfrage

Liefert der native WASAPI-Capture-Vertrag fuer den dem bisherigen Audiogeraet
`5` eindeutig zugeordneten Aufnahme-Endpunkt bei exakt 48.000 Hz eine rohe,
paketbezogene und lueckenlose Folge aus Paketgroesse, Position des ersten
Frames, korrelierter QPC-Position und Statusflags?

Der Probe prueft nur die technische Bereitstellung dieser Metadaten. Eine
gueltige Folge waere ein Kandidat fuer eine spaetere Quellenstuetzenpruefung,
aber noch keine Quellenstuetze, Organismuszeit oder MCM-Feldzeit.

## Vorhandene Negativbaseline

Der bestehende PortAudio-/`sounddevice`-Audit bleibt unveraendert die
Negativbaseline. Er erfasst je Callback:

- `inputBufferAdcTime`;
- `currentTime`;
- Organismus-Callbackzeit;
- Callback-Framezahl;
- Input-Overflow.

`AudioCallbackTiming` besitzt keine native Paketposition und keine
paketbezogene QPC-Position. `organism_support_is_mapped` bleibt `False`. Die
Lauf-109-bis-117-Befunde erlauben weder Rueckrechnung aus Latenz oder
Framezahl noch eine Reparatur der PortAudio-Zeitfelder.

## Technischer Kandidat

Der spaetere Probe darf ausschliesslich
`IAudioCaptureClient::GetBuffer` verwenden und pro erfolgreich geliefertem
Paket diese Werte unveraendert ausgeben:

```text
packet_index
pNumFramesToRead
pu64DevicePosition
pu64QPCPosition
pdwFlags
GetBuffer-HRESULT
ReleaseBuffer-HRESULT
```

Zusaetzlich duerfen nur unveraenderliche Laufmetadaten ausgegeben werden:
native Endpoint-ID, Anzeigename, Datenflussrichtung, Share-Mode,
angefordertes und tatsaechlich initialisiertes Audioformat sowie Start- und
Abbruchgrund. Audiodaten werden weder gespeichert noch als Forschungswert
ausgewertet.

## Verbindliche Geraetezuordnung

Der `sounddevice`-Index `5` ist keine native WASAPI-Endpoint-ID und darf nicht
als solche verwendet werden. Vor jeder Implementierung oder Ausfuehrung muss
eine separate Inventarausgabe genau einen aktiven Capture-Endpunkt ausweisen:

- vollstaendige, nicht gekuerzte WASAPI-Endpoint-ID;
- exakter Anzeigename;
- Capture-Datenflussrichtung;
- aktive Geraeterolle und Kanalzahl;
- daneben die unveraenderten lokalen Metadaten des bisherigen Geraets `5`.

Die native Endpoint-ID muss vor dem Lauf explizit festgelegt werden. Fuzzy
Matching, Teilstrings, Defaultgeraet-Fallback oder automatische Wahl des
ersten passenden Endpunkts sind unzulaessig. Ist die Zuordnung nicht
eindeutig, endet der Probe vor dem Oeffnen des Streams.

## Festes Aufnahmeformat

Vorregistriert ist genau ein Format:

```text
Abtastrate:       48000 Hz
Kanaele:          1
Sampleformat:     IEEE float32
Share-Mode:       shared
Loopback:         nein
Formatkonversion: nein
```

`IAudioClient::IsFormatSupported` muss dieses exakte Format bestaetigen.
`IAudioClient::Initialize` muss mit demselben Format erfolgreich sein. Ein
vom System vorgeschlagenes Alternativformat, Resampling, Kanalumbau oder ein
Wechsel in Exclusive Mode ist kein Ersatzarm und beendet den Probe.

## Begrenzter Ablauf eines spaeteren Probes

Ein spaeterer, separat freigegebener Lauf darf genau so ablaufen:

1. COM initialisieren und den vorregistrierten Endpoint ueber seine exakte ID
   aktivieren.
2. Das feste 48-kHz-Format pruefen und den Shared-Mode-Capture-Stream
   initialisieren.
3. `IAudioCaptureClient` beziehen und den Stream starten.
4. Maximal 100 nichtleere Pakete erfassen; nach 10 Sekunden ohne Erreichen
   dieser Grenze abbrechen.
5. Bei jedem erfolgreichen `GetBuffer` alle vorregistrierten Rohfelder vor
   jeder Ableitung erfassen und das vollstaendige Paket mit
   `ReleaseBuffer(pNumFramesToRead)` freigeben.
6. Stream stoppen und genau eine JSON-Ausgabe mit Laufmetadaten,
   Paketdatensaetzen und einem eindeutigen Endgrund schreiben.

Ein leeres Buffer-Ergebnis ist kein Audiopaket und erhoeht den Paketindex
nicht. Es darf nur als unveraenderter HRESULT-Zaehler in den Laufmetadaten
erscheinen.

## Vorregistrierte technische Pruefungen

Die spaetere Auswertung darf nur folgende exakte Eigenschaften berichten:

1. Alle 100 Paketdatensaetze besitzen nichtnegative Ganzzahlen fuer
   Framezahl, Device-Position, QPC-Position und Flags.
2. Jede Paketgroesse ist groesser als null.
3. Fuer jedes Folgepaket ohne vorherigen Abbruch gilt exakt:

   ```text
   device_position[i]
   == device_position[i - 1] + frame_count[i - 1]
   ```

4. Die Device-Positionen und QPC-Positionen sind strikt monoton.
5. Kein Paket traegt `AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY` oder
   `AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR`.
6. Kein COM-, WASAPI-, Buffer- oder Release-Aufruf endet mit einem
   Fehler-HRESULT.

Es gibt keine numerische Toleranz. QPC-Differenzen, Paketgroessen und
Device-Positionsdifferenzen werden roh berichtet. Sie duerfen weder geglaettet
noch auf eine erwartete Rate korrigiert werden.

`AUDCLNT_BUFFERFLAGS_SILENT` ist kein Zeitfehler. Das Flag wird roh erfasst;
der Paketinhalt wird weiterhin nicht gespeichert oder interpretiert.

## Harte Abbruchkriterien

Der spaetere Probe endet sofort und ohne positive Kandidatenaussage, wenn
mindestens eine Bedingung eintritt:

- native Endpoint-Zuordnung fehlt, ist mehrdeutig oder weicht von der
  vorregistrierten ID ab;
- das exakte 48-kHz-Format wird nicht unterstuetzt oder nicht initialisiert;
- ein erforderlicher COM- oder WASAPI-Aufruf scheitert;
- `DATA_DISCONTINUITY` oder `TIMESTAMP_ERROR` tritt auf;
- eine Paketgroesse ist null, nachdem `GetBuffer` ein nichtleeres Paket
  gemeldet hat;
- Device- oder QPC-Position ist nicht strikt monoton;
- die Device-Position schliesst nicht exakt an das vorherige Paketende an;
- `ReleaseBuffer` scheitert oder wird nicht im selben Thread dem zugehoerigen
  `GetBuffer` zugeordnet;
- 100 nichtleere Pakete werden nicht innerhalb von 10 Sekunden erreicht;
- Rohwerte koennen nicht vor jeder Auswertung unveraendert ausgegeben werden;
- die Umsetzung erfordert Glattung, Toleranz, Rueckrechnung, Ersatzzeit,
  Formatkonversion oder eine Rezeptor- beziehungsweise Feldanbindung.

Ein Abbruch ist ein technischer Grenzbefund fuer diesen Endpoint, dieses
Format und diesen Probe. Er beweist keine allgemeine Unmoeglichkeit nativer
Audio-Quellenpositionen.

## Zulaessige Gegenbaselines

- **B0, bestehender Audit:** unveraenderte PortAudio-/`sounddevice`-Rohfelder
  aus den bisherigen Laeufen; keine native Paketposition.
- **B1, Schemakontrolle:** rein synthetische Paketfolgen pruefen spaeter nur,
  ob fehlende Felder, Fehlerflags, Rueckspruenge, Luecken und fehlerhafte
  `ReleaseBuffer`-Zuordnung strikt abgelehnt werden.
- **B2, nativer Rohprobe:** genau der oben festgelegte Endpoint, das feste
  Format und die begrenzte Paketanzahl.

B1 ist keine positive Quellenbaseline. Weitere Geraete, Raten, Formate,
Blockgroessen oder Share-Modes sind nicht Bestandteil dieser
Vorregistrierung.

## Verbotene Ableitungen

- kein Samplezaehler aus kumulierten Paketgroessen als Ersatz fuer
  `pu64DevicePosition`;
- keine Zeit aus Framezahl, QPC-Differenz, Latenz, Callbackabschluss oder
  nomineller Rate rekonstruieren;
- keine Ausreisserkorrektur, Glattung, Toleranz oder nachtraegliche Auswahl;
- keine Wiederholung mit veraenderten Parametern nach Einsicht in Rohwerte;
- keine Abbildung auf Organismuszeit;
- keine Feld-, Rezeptor- oder Audio-Video-Runtimeanbindung;
- keine Aussage ueber MCM-Memory, Organisation, Semantik oder Topologie.

## Auswertungsentscheidung

Der spaetere reale Probe darf hoechstens zu einer dieser Entscheidungen
fuehren:

```text
TECHNISCH_NEGATIV:
  mindestens ein Abbruchkriterium wurde erreicht

PAKETPOSITION_KANDIDAT:
  der begrenzte Lauf erfuellte alle exakten Rohmetadatenpruefungen
```

`PAKETPOSITION_KANDIDAT` bedeutet nur, dass eine native Paketpositionsfolge
fuer eine nachfolgende, separat vorregistrierte Quellenstuetzenpruefung
vorliegt. Der Status darf nicht als Quellenstuetze, Feldzeit oder
Organismuszeit bezeichnet werden.

## Ergebnis von Lauf 118

Der Implementierungs- und Abbruchvertrag ist formuliert. Es wurde kein
Messlauf ausgefuehrt, daher liegen keine neuen Messwerte und kein positiver
Kandidat vor. Forschung 030 bleibt gesperrt.

Die bestehende Mechanik reicht als Negativbaseline und zum Vergleich der
oeffentlichen Rollen aus. Fuer die eigentliche native Erfassung reicht sie
nicht, weil PortAudio/`sounddevice` die paketbezogene Device- und QPC-Position
nicht exponiert. Eine minimale native Werkzeugerweiterung bleibt von einer
gesonderten Freigabe abhaengig.

## Tatsaechlich verwendete Quellen

- Benutzerfreigabe zu Lauf 118;
- `docs/architektur/031_FELDZEITUEBERGABE.md`;
- `docs/architektur/036_BEOBACHTUNGSGRENZE_STATT_FELDTAKT.md`;
- `docs/forschung/031_ORDNUNG_OFFENE_LUECKE_FORSCHUNG_030.md`;
- `mcm_field_organism/adapter_timing_capability.py`;
- `tools/run_live_adapter_timing_capability_audit.py`;
- Microsoft, `IAudioCaptureClient::GetBuffer`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-getbuffer>;
- Microsoft, `IAudioClient::Initialize`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudioclient-initialize>;
- Microsoft, `IAudioCaptureClient::ReleaseBuffer`:
  <https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-releasebuffer>.

MINI_DIO- und externe MCM-Mechanikquellen wurden nicht verwendet.
