# S2-NI: auditive Rezeptor-/Kontakt-Ausgangsskala

Status: `STATISCHER_VORSCHLAG_KEINE_IMPLEMENTIERUNGSFREIGABE`.
Stand: 2026-09-07. Keine Lauf-ID, keine neue Messung.

## 1. Grenze und Gegenstand

Die [e02-Diagnose](../reports/s2nh/s2nh-e02-audio-endpoint-diagnostic-20260907-01/BEFUND.md)
ist abgeschlossen. Sie belegt einen endlichen Wert ausserhalb der Kontakt-
Normalform in einer neuen Reproduktion. Ihr Maximum begruendet **keinen**
Skalierungsfaktor. S2-NH bleibt `NOT_EVALUABLE`, S2-NG bleibt historisch gueltig.
Beide Hauptgates bleiben `False`; keine Wiederholung oder Quellenkorrektur.

Untersucht wird nur eine profilgebundene auditive Ausgangsskala. Grundlage:
[LogSpectralReceptor](../mcm_field_organism/log_spectral_receptor.py), insbesondere
Zeilen 85-94, 107-134 und 140-144; [Kontaktvertrag](../mcm_field_organism/receptor_contract.py),
Zeilen 29-45 und 197-210. Gueltiger PCM-Eingang bedeutet endlich und `abs(x)<=1`;
die aktuelle spektrale Ausgabe ist dagegen nicht auf `1` begrenzt.

Die lokal gelesene NumPy-2.4.4-Implementierung bestaetigt das symmetrische Hann-
Fenster (`numpy/lib/_function_base_impl.py:3341`) und die unskalierte Vorwaerts-
FFT bei `norm=None` (`numpy/fft/_pocketfft.py:68`). Keine Bibliothek ausgefuehrt.

## 2. Quellenunabhaengige Schranke in exakter Arithmetik

Seien `N=4800`, `x_n` reell mit `|x_n|<=1`, `w_n` das symmetrische Hann-Fenster,
`W=sum(w_n)>0`, `Q=sum(w_n^2)` und `F_k=DFT(w*x)_k` die unskalierte DFT.
Mit Filtergewicht `a_bk` berechnet der vorhandene Code je Band:

```text
w_n = (1-cos(2*pi*n/(N-1)))/2
E_b = (2/W) * sqrt(sum_k a_bk^2 * |F_k|^2)
```

Die Wurzel aggregiert quadrierte gewichtete Spektralamplituden; es handelt
sich nicht um einen auf Eins normierten Mittelwert. Dreiecksgewichte liegen
in exakter Arithmetik in `[0,1]`. Filterbankueberlappung ist erlaubt; fuer die
Schranke eines einzelnen Bandes wird keine Disjunktheit angenommen.

Eine allgemeine, oft grobe Schranke folgt aus `|F_k|<=W`:
`E_b <= 2*sqrt(sum_k a_bk^2)`. Sie benoetigt keine Korpuswerte.
Fuer das gebundene Profil ist folgende Parseval-Schranke erheblich geeigneter:

```text
sum_{k=0}^{N-1} |F_k|^2 = N * sum_n |w_n*x_n|^2 <= N*Q
sum_{k=1}^{N/2-1} |F_k|^2
  = (N*sum_n |w_n*x_n|^2 - |F_0|^2 - |F_{N/2}|^2)/2 <= N*Q/2
E_b^2 <= (4/W^2) * N*Q/2 = 2*N*Q/W^2
```

Voraussetzungen der zweiten Zeile: reeller Eingang, gerades `N`, konjugierte
DFT-Symmetrie. Im Default-Live-Profil sind alle Gewichte bei DC und Nyquist
Null: `50 Hz <=` Filterstuetzung `<= 18000 Hz < 24000 Hz`. Auch die besondere
`isclose(..., atol=1e-12, rtol=0)`-Behandlung der Randbaender erfasst hier weder
DC noch Nyquist. Die einseitige FFT darf deshalb ohne deren Energie gebunden
werden. Diese Eigenschaft muss bei anderen Profilen erneut geprueft werden.

Fuer das symmetrische Hann-Fenster mit `N>=4` gelten die endlichen Summen
`W=(N-1)/2`, `Q=3*(N-1)/8`. Damit folgt fuer **jedes** gueltige PCM-Fenster:

```text
0 <= E_b <= B = sqrt(3*N/(N-1)) = sqrt(14400/4799) < 2
```

Das ist eine obere Schranke, kein behauptetes erreichbares Maximum. Sie ist
unabhaengig von Frequenz, Phase, Quelle, Ereignis, Korpus und Trefferergebnis.
Der Hop `480` bestimmt die Fensterfolge, nicht diese Amplitudenschranke.
Ohne nachgewiesenen DC-/Nyquist-Ausschluss bleibt aus Parseval nur die groebere
Schranke `2*sqrt(N*Q)/W`; die hier empfohlene Skalierung waere dann neu zu begruenden.

## 3. Empfehlung und offene numerische Grenze

**Empfehlung als spaeter zu qualifizierender Kandidat:** ein neues, explizit
versioniertes Ausgangsprofil mit `z_b = 0.5 * E_b`, einheitlich fuer alle
48 Baender, nach derselben bestehenden Spektralrechnung. `2` ist eine einfache
konservative Obergrenze der hergeleiteten Profilschranke; `0.5` ist exakt
binaer darstellbar. Es ist weder eine Eingangsabschwachung noch eine Ableitung
aus dem NH-Maximum. In exakter Arithmetik gilt `z_b <= B/2 < 1`.

Diese Groessenordnung ist praktisch plausibel: kein Faktor, der mit der
Fensterlaenge gegen Null geht, keine zusaetzliche Dimension und keine neuen
zustandsbehafteten Schritte. Funktionale Brauchbarkeit ist damit nicht bewiesen.
Die knappere Skalierung `1/B` wird nicht empfohlen: Sie laesst an der
analytischen Grenze keine Reserve fuer numerische Abweichungen.

**Offen bleibt die maschinelle Garantie.** NumPy-Hann, Filtergewichte,
Fenstermultiplikation, FFT, Betrag, Quadrate, Summation und Wurzel runden.
Der Beweis fuer ideale reelle Operationen ist kein verifizierter Fehlerbound
dieser gesamten Binary64-Implementierung. Vor einer universellen Zusage ist
quellenunabhaengig abzusichern, dass der tatsaechliche endliche Rohwert unter
`2` bleibt, etwa durch eine begruendete absolute Gesamtfehlergrenze kleiner
als `2-B`, bezogen auf die ideale Rechnung. Dafuer liegt hier kein Zertifikat
vor; ein bestandener endlicher Testkorpus ersetzt diesen Nachweis nicht.

Halbierung normaler Binary64-Werte ist binaer einfach; Subnormalzahlen und
Unterlauf bleiben gesondert zu pruefen. Weder allgemeine Bitinvertierbarkeit
noch uneingeschraenkte Werterhaltung werden behauptet. Nichtendlichkeit oder
verfehlte Normalform bleibt fail-closed, ohne Clipping oder Nachskalierung.
Kann die numerische Absicherung nicht erbracht werden, bleibt die universelle
Kontaktkompatibilitaet offen; kein stiller Ersatzfaktor oder Backendwechsel.

## 4. Verbindliche Folgewirkungen einer spaeteren Aenderung

- Die Skalierung gehoert vor die gemeinsame kanonische Wahrnehmungsbindung.
  Feld und Memory muessen dieselben 48 skalierten Audio- und unveraenderten
  288 Visualwerte erhalten, als unabhaengige Geschwisterprojektionen. Nur im
  Kontaktadapter oder nur im Memory zu skalieren waere unzulaessig.
- Die neue Ausgangssemantik braucht eine unterscheidbare Profil-/Versions-
  und Digestbindung, auch bei gleichen Frequenzcarriern und Dimensionen.
  Bestehende Geometrie-/Profilbindungen duerfen nicht denselben Namen fuer
  verschiedene Skalen vortaeuschen. Alte/neue Zustaende nicht mischen oder
  nachtraeglich umetikettieren; historische Rezeptorbelege nicht umschreiben.
- In reeller Arithmetik halbieren sich reine auditive L1- und maximale
  Banddistanzen zwischen entsprechend skalierten Vektoren. Numerische
  Bitgleichheit historischer Rechenketten folgt daraus nicht. Digests und
  Profilabhaengigkeiten aendern sich; identische Nullwerte koennen erhalten bleiben.
- Unveraenderte Zahlenwerte `0.2` und `0.02` wuerden in der alten Audioskala
  doppelt so breite Abstaende zulassen. Das betrifft Fast-Zuordnung, PPB-
  Bildung und Abruf, nicht nur die Kontaktvalidierung. Auch `ALL_BANDS_24`
  waere damit funktional neu zu qualifizieren. Keine automatische Halbierung
  oder Neukalibrierung von Schwellen wird hier freigegeben.
- Feldanregung und auditive Gewichtung gegenueber unveraenderten Visualwerten
  aendern sich. Ein linearer Skalierungsbeweis begruendet keine skaleninvariante
  Feldtrajektorie, keine identischen Supports und keine gleichen Treffer.
  Historische Qualifikationen und S2-NG bleiben fuer ihre alten Profile gueltig,
  uebertragen sich aber nicht automatisch. 336 Werte bedeuten nicht alte Semantik.

## 5. Alternative: Kontaktbereich erweitern

Die alte Rezeptorskala zu erhalten und den Kontaktbereich profilbezogen zu
erweitern waere eine andere Architekturentscheidung. Eine Aenderung nur in
`_normalized_values` genuegt nicht: nachgelagerte Normalformvalidatoren,
Memoryprofile und -zustandsbindungen, Dock-/Feldgrenzen sowie numerische
Ressourcenannahmen waeren zu pruefen. Ein allgemeiner Bereich `[-2,2]` wuerde
ausserdem andere Modalitaeten betreffen, obwohl nur Audio den Anlass liefert.
Die maschinelle Schrankenfrage verschwindet dadurch ebenfalls nicht.
Diese Alternative wird wegen der breiteren Vertragswirkung nicht bevorzugt
und hier nicht umgesetzt. Ein offener oder unbegrenzter Wertebereich ist
keine Empfehlung.

## 6. Notwendige spaetere Pruefgrenzen

Nach separater Analystenentscheidung: profil-/backendgebundene numerische
Absicherung und kleine neutrale Qualifikation der festen Ausgangsprojektion.
Zu binden sind Hann-/Gewichtsform, FFT-Norm, DC-/Nyquist-Ausschluss,
Rechenreihenfolge, Runtimeidentitaet, Normal-/Subnormalbehandlung und Digests.
Neutrale Grenzfaelle umfassen Null, konstante und alternierende Vollaussteuerung,
Impulse sowie vorab feste spektrale Mischungen und Phasen; keine Suche nach
einem passenden Korpus. Technische Akzeptanz bleibt endlich und in Normalform.

Danach waeren getrennt erforderlich: gleiche kanonische Projektion an beide
Zweige, erneute Feld-/Memory-/Abrufqualifikation und prospektive funktionale
Bewertung mit ausdruecklich entschiedener Schwellenbedeutung. Gute numerische
Grenzen allein oeffnen weder NH noch einen neuen Runtimevergleich.

Heute wurden ausschliesslich Dateien gelesen, die obige Algebra hergeleitet
und dieser Vertrag dokumentiert. Keine Projektimporte, Tests, Payloads,
Rezeptoraufrufe, neuen Korpusberechnungen, Codeaenderungen oder Gateumschaltungen.
Historische Belege und Bootstrap bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung ueber die
feste profilversionierte Ausgangshalbierung und ihre numerischen sowie
funktionalen Qualifikationsgrenzen weiter.
