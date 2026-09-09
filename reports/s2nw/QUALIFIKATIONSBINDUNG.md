# S2-NW: vorab gebundene rezeptorfreie Quellenqualifikation

Eigene ID `s2nw-source-binding-qualification-20260909-01`; genau ein
Aufruf `C:/Python314/python.exe -m reports.s2nw.qualify_once` aus workspace.
Ein unittest-Prozess mit `-v -f`, kein Retry. Historische Qualifikationen
werden nicht wiederholt. Quellhashes und Testnamen vor Prozessstart in
preregistration.json, danach dieselben Hashes und Exit-Code in result.json.

20 feste neutrale Gruppen: Quelleninventar; native Zeiten; getrennte
Exaktidentitaeten; Phasen/Nullpartial; Gruppen-/Gain-/Lokalzeitfolge;
einmalige Float32-Rundung; Partialreihenfolge; unabhaengige Vollpruefung;
Quellen-/Zeitmanipulation; Praefix-/Prognosestellen; funktionale Eingaben;
getrennte neun Kriterien; Ressourcen; Unveraenderlichkeit/Profil/Digest;
Built-in-math; Fail-closed/Ausschluesse; Updatepositionen; Freeze-Grenze;
kein vorgegebener Lernkoeffizient; Zaehler/Budget/Phasenfreigaben.

NW- und historische NU-Payloadgeneratoren sind in allen Testkoerpern
gesperrt. Synthetische Payloadhash-Tokens stammen ausschliesslich aus
Metadaten, nicht aus NW-PCM. Nur sechs neutrale Samples (24 Byte), in zwei
Dreiergruppen, werden durch den kleinen Renderhelfer erzeugt; nie ein
vollstaendiges Fenster. Hoechstens 12 neutrale Payloadbytes gleichzeitig;
64 sin-Aufrufe und 32.768 Metadaten-Digestpruefungen als Grenzen.
Keine NW-Payloads, Rezeptoren, NJ, Koeffizienten, Prognosen, Fehlerauswertung
oder Systemaufrufe. Neue Formeln werden nur als literale Metadaten gebunden.

Nach Bestehen separat genau ein Vorversiegelungsaufruf unter
`s2nw-source-preseal-20260909-01`: 26 Fenster, 124.800 Samples, 499.200
erzeugte PCM-Bytes, hoechstens ein 19.200-Byte-Payload gleichzeitig,
keine Rohdatenablage. Jede Plan-/Metadatenwurzel maximal 65.536 Byte,
Verifikationsbeleg maximal 262.144 Byte. Danach eine unabhaengige lesende
Bindungspruefung ohne PCM-Regeneration. Bei Fehler stoppen.

Diese Qualifikation prueft noch keinen Vorhersagecontroller. Die spaetere
Prognose-vor-Ziel-/Update-nach-Ziel-/Freeze-Grenze ist nur vorab beschrieben,
nicht bereits funktional qualifiziert. Hauptgate bleibt False; ME/MI gesperrt.
