# S2-SP: OA-Materialisierungsadapter – fokussierte Neutralqualifikation

Qualifikations-ID: `S2SP-OA-ADAPTER-QUAL-20260919-01`.

Der einmalige neutrale Aufruf
`python -B -m unittest tests.test_s2sp_oa_materialization_adapter -v`
bestand mit `2/2`.

- Ein vollständiges OA-AV-Ereignis wird über `Materializer.next()` genau
  einmal materialisiert: ein Audio- und ein visueller Rezeptoraufruf sowie
  genau eine NJ-Projektion. Der Adapter übernimmt den daraus entstandenen
  Halbprofil-Pair ohne weitere Projektion und erhält PCM-/RGB-Digests,
  Halbprofilbindung, Feldzeit und Paarzeit.
- Ein visueller Cue wird vor jedem Payloadzugriff mit
  `OA_AV_EVENT_REQUIRED` abgewiesen. Der Adapter ist ausschließlich für
  vollständige AV-Formationen bestimmt.

Die konkrete V2-Folge mit 18 Formationen und zwei Hinweisen, ihre
Lifecycle-Auswertung und der Zweiarmvergleich wurden nicht ausgeführt. Sie
benötigen eine eigene vollständige Anschlussqualifikation über die gebundene
20-Ereignis-Hülle.

## Nachtrag: unzulässiger Sammelaufruf

Nach Ergänzung eines dritten neutralen End-to-End-Tests wurde derselbe
Testmodulaufruf erneut ausgeführt. Der technische Lauf endete mit `3/3`,
wiederholte dabei jedoch die bereits unter dieser Qualifikations-ID gebuchten
beiden Adapterkontrollen. Er ist daher keine neue, protokollkonforme
Qualifikation und darf weder die bestehende `2/2`-Teilqualifikation noch eine
vollständige V2-Anschlussqualifikation ersetzen.

Der neue Test belegt nur technisch, dass ein bereits materialisiertes
Halbprofil-Pair zwei getrennte, frische Vergleichsarme fortschreiben kann.
Die gebundene 20-Ereignis-Hülle wurde nicht neutral qualifiziert; es wurden
keine V2-Quellen materialisiert und kein V2-Hauptlauf ausgeführt. Nach diesem
Protokollverstoß wurde angehalten; es erfolgt kein Retry.
