# S2-NU: einmalige Rezeptor-/NJ-Materialisierung

## Technischer Abschluss

Lauf-ID: `s2nu-receptor-nj-materialization-20260909-01`.
Genau ein Aufruf von `python -m reports.s2nu.materialize_once`, Exit-Code `0`.
Ergebnis: **RECEPTOR_NJ_MATERIALIZATION_COMPLETE**; Fehlerbeleg `null`.
Anschliessend genau eine unabhaengige read-only Pruefung:
**S2NU_MATERIALIZATION_VALID**. Kein Probelauf, Testaufruf oder Retry.

| Gebundener Umfang | Tatsaechlich abgeschlossen |
| --- | --- |
| PCM-Regenerationen / Payloadpruefungen vor Analyse | 30 / 30 |
| Direkte `LogSpectralReceptor.analyze`-Aufrufe | 30 |
| NJ-Endpunktprojektionen | 30 |
| Gespeicherte Rohwerte / Halbwerte | 1.440 / 1.440 |
| Vollstaendig gebundene Fenster | 30 |
| Unabhaengig vorwaerts gepruefte Halbierungen | 1.440 |
| Rollende Hops / Kontaktframe-Aufrufe | 0 / 0 |
| Gespeicherte PCM-Payloads | 0 |

Alle Fenster `nu-s01-w00` bis `nu-s06-w04` wurden in versiegelter Reihenfolge
mit ihren eigenen nativen Fenstern und Snapshotindizes verarbeitet. Der
PCM-SHA-256 musste jeweils vor `analyze` zur Quellenbindung passen.
Bytegleiche Fenster erhielten eigene Analyse- und Projektionsaufrufe;
keine Deduplizierung oder Uebernahme frueher erzeugter Rezeptorwerte.

## Unveraenderte Herkunft und Anschluss

Die historische NU-Vorversiegelung wurde nur gelesen. Gebunden bleiben:

- Ausfuehrungsdigest: `1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7`.
- Siegeldigest: `0dea5839d814c50c82a2858fca00632b0cdcbedda6576f28a0031f687f313a13`.
- Vorversiegelungspruefung: `069b9892cdd9d872f0d861dd570e2a4240e3ac1d99ee1502d77111a8c8f18e68`.
- Raw-Profil: `5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7`.
- NJ-Halbprofil: `4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f`.

Die separate NU-Aufrufbindung uebernimmt die vorhandene direkte
NT-Materialisierungs-/Belegform, ohne einen historischen Einstieg aufzurufen
oder umzuwidmen. Gemeinsame Kanonisierung, Byte-Digest und atomare Publikation
werden unveraendert wiederverwendet. Die versiegelte NU-Generatorfunktion,
Rezeptoren und NJ blieben unveraendert. Kein HearingPath-/Rolling-Aufruf;
die vorhandenen Rohzustandstypen tragen nur die reduzierte Ausgabe.

Neue Anschlussdateien, vor der Analyse gebunden:

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2nu_private_receptor_materialization.py` | `e2feb9cf4e1fe543d04d4e60443257827c7508e79b1e0037686491872149f0df` |
| `tools/_s2nu_private_materialization_verification.py` | `85ae7b8a2e6fe938b5a5afec645bfe961f89e378f934d7cf4da6c718f0c6156d` |
| `reports/s2nu/materialize_once.py` | `8344d17e482d7ad8b441f22760dea48a1900422e18854dab801bf17f3697afd5` |

Alle 21 gebundenen Dokument-, Code- und Vorversiegelungsdateien sind vor und
nach Ausfuehrung identisch. Vollstaendige Bindungen sowie Interpreter-/
NumPy-Identitaet stehen in [Vorregistrierung](preregistration.json) und
[Gesamtbeleg](result.json). Keine Quellenkorrektur, Abschwaechung oder Normalisierung.

## Numerik und unabhaengige Pruefung

Je Fenster gespeichert: urspruenglicher reduzierter Rohzustand, NJ-Projektion,
Source-/Recipe-/PCM-Digests, native Zeiten, Carrier-/Profilbindung,
kanonische Zustands-/Projektionsdigests sowie Binary64-Hexdarstellungen und
SHA-256 der `<48d`-Bytes beider Skalen. Rohwerte werden nicht aus Halbwerten
rekonstruiert. Alle Rohwerte sind endlich und nichtnegativ, alle Halbwerte
endlich und innerhalb `[0,1]`.

Die getrennte Pruefung hat jede gespeicherte Halbierung mit `raw * 0.5`
vorwaerts nachgerechnet und deren `<d`-Bytes exakt verglichen. Keine Toleranz
oder Rundungskorrektur. Roh-/Halb-Subnormalmarker und Unterlaufmarker sind
gespeichert, geprueft und in allen 30 Belegen leer. Das ist ein Befund fuer
diese Ausfuehrung, kein universeller Gleitkommanachweis.

Reine Bindungspruefungen betreffen Quellen-/Payloadhashlinks, Reihenfolge,
Fenster und native Indizes, Profile/Carrier, Codeidentitaeten, Digests,
Zaehler und Unveraenderlichkeit. Die Offline-Pruefung hat weder PCM
regeneriert noch FFT, Filterbank, `analyze` oder NJ erneut aufgerufen.
Sie prueft daher nicht unabhaengig die numerische FFT-Ableitung aus den
Rohbytes; diese ist durch den protokollierten einmaligen Rezeptorpfad gebunden.

## Ergebnisbindungen und Grenzen

- Ergebnisdigest: `4785e577139ff597564b1e0ceae63d3793e00a47188d5574af445025f4b37c13`.
- Ergebnisdatei-SHA-256 vor/nach Pruefung: `93c8141a959ee6ffc656fed8053f740bb8e6356779ee6fc18e1aa93cdf4bc1d3`.
- [Verifikationsdigest](verification.json): `ffb58bff7ef45caee35624d62040a1b045c2d24472feff98db7ecd5a9a4c32bb`.
- Gesamtbeleg: 289.226 Byte, unter 2.097.152 Byte.
- Vorregistrierung: 9.965 Byte, unter 65.536 Byte.
- Verifikationsbeleg: 1.101 Byte, unter 262.144 Byte.
- Hoechstens ein PCM-Fenster mit 19.200 Byte; keine Rohpayloadablage.

Die Verifikationsarbeit war separat auf 30 Belege und 1.440
Vorwaertshalbierungen begrenzt. Zeitliche Differenzen, `step`, `T`,
Anfang-/Endabstaende, Multisetvergleiche und die fuenf Ordnungskriterien
blieben vollstaendig unausgefuehrt. Keine numerische Gegenueberstellung
bytegleicher Fenster; deren spaetere Kontrollgleichheit wird nicht behauptet.
Memory-, Feld-, Kontext- und Runtimeaufrufe jeweils `0`.

Materialisierungs- und Quellengate stehen nach dem Lauf `False`; historische
Gates wurden nicht geoeffnet. ME/MI und saemtliche historischen Befunde
bleiben unveraendert. Fremde Aenderungen und Bootstrap sind ausgeschlossen.

**Bestaetigt ist die technische Materialisierung, nicht Verlaufstrennung,
Quellenfortsetzung oder Lernbindung.** Der naechste Vorschlag betrifft allein
die Analystenpruefung dieses Belegs und die separate Freigabe einer neutralen
Vergleichsanbindung; keine unmittelbare Verlaufsauswertung.
