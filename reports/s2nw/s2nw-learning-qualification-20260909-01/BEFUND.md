# S2-NW: neutrale Lern-/Prognoseanbindung qualifiziert

Status: `S2NW_LEARNING_QUALIFIED`, **28/28**, Exit-Code `0`.
Lauf-ID: `s2nw-learning-qualification-20260909-01`.
Genau ein vorab gebundener Qualifikationsaufruf, kein Retry und kein
realer NW-Lern-/Transferlauf. Die vorherige Quellenqualifikation wurde
nicht wiederholt. Nach dem Aufruf wurden ausschliesslich Belege gelesen
und dieser Abschluss dokumentiert.

## Bindungen und Umfang

- [Preregistrierung](preregistration.json): 28 Testnamen, unveraenderte
  Einzel-/Gesamtbudgets, Python-/NumPy-Umgebung und Quellhashes vor dem Aufruf.
- [Testprotokoll](stderr.txt): alle 28 Testkoerper erreicht und bestanden.
- [Ergebnis](result.json): Vor-/Nachhashes identisch; NW-, Quellen- und
  historisches NV-Gate abschliessend `False`.
- [Vollstaendige neutrale Huelle](neutral-envelope.json): 444.129 Byte
  gegen maximal 2.097.152 Byte, einschliesslich 26 synthetischer Fenster,
  16 Prognosestellen, Lern-/Freeze-/Closeketten und Codebindungen.

Ergebnisdigest:
`9ae0be9c02483365db0344ae7c28563e80032ff75dae94b44256c75f0e195a18`.
Huellendatei-SHA-256:
`e5c841fdedf66a3af5fa5aa8fb5c72e948e5568226ac61ac90de5661a53ab545`.
Alle individuellen Quellhashes stehen unverkuerzt in Preregistrierung und
Ergebnis; die historischen Quellen-/Plan-/Siegeldateien sind darunter.

Vier kleine private NW-Module ergaenzen den bestehenden NV-Weg:
Lernarithmetik, praefixgebundener Ablauf, unabhaengige Direktnachrechnung/
Verifikation und getrennte Bewertung. NV-Rezeptoradapter und atomare IO
werden wiederverwendet, LINEAR/PERSIST unveraendert aufgerufen. Keine
historische Hauptfunktion wurde umgewidmet; kein neuer Recorder.

## Tatsaechlich erreichte Kontrollen

| Grenze | Neutraler Nachweis |
| --- | --- |
| Initialisierung/Rechnung | n=0 und drei positive Binary64-Nullwerte; aufsteigende Bandakkumulation, getrennte Operationen und unabhaengiger Direktlerner aus eigenem Nullzustand |
| Update nach Beobachtung | Vier Updates erst nach Rueckkehr des Zielreaders und Bindung der Fehler; Aufruf vor Beobachtung mit `TARGET_NOT_OBSERVED` abgewiesen |
| Prognose vor Ziel | Fehlende/veraenderte Prognose und vorzeitiger Zielzugriff vor Readeraufruf abgewiesen; administrative Quellenkennungen veraendern identische funktionale Prognosen nicht |
| Echte neutrale Adaptergrenze | Sechs direkte Analysen und sechs NJ-Projektionen aus konstanten neutralen PCM-Fenstern; Generator kontrolliert bei jedem Ziel die bereits gebundene Prognose und bisherigen Updatezaehler |
| Freeze/Retention | Freeze vor vier Updates abgewiesen; danach dieselbe unveraenderliche Bindung fuer alle zwoelf synthetischen Pruefprognosen, Testupdates abgewiesen, Praefix pro Folge frisch |
| Kette/Manipulation | Vorzustand, Beobachtungsdigest, Freeze-Vorgaenger und unerlaubter Testupdate separat typisiert abgewiesen; Offline-Nachrechnung reproduziert vier Updates pro Arm |
| Zahlen | Nullnenner, Produktunterlauf, nichtendliche Eingaben/Zustaende; endliche Prognosen 4.0 und -3.0 bleiben ungeclippt und werden bewertet |
| Negative Funktion | Konstante Nullfolge technisch verifiziert, Divisionen 0, funktional `FALSIFIED`; gueltiger negativer Befund ist kein technischer Fehler |
| Auswertung | Training getrennt von Transfer, Gewinne gegen PERSIST und LINEAR separat, erste Wechselverluste sichtbar, keine Kompensation oder nachtraegliche Armwahl |
| Beleg/Lifecycle | Vollstaendige Huelle, Groessen-/Arbeitsueberschreitung, Schreibkonflikt, einmalige Verifikationsfreigabe, fehlende Belege und phasengenauer Fehlerabschluss |

Im gespeicherten **synthetischen**, nicht realen NW-Beispiel entstanden
`Sxx=0.99609375`, `Sxy=0.498046875`, `alpha=0.5`, `n=4` in beiden
unabhaengigen Lernern. Diese Werte sind keine Lernvorgabe und keine Prognose
fuer den versiegelten NW-Korpus. Der Freeze-Digest ist dort
`c973f734f69681ca687d1bc715ed0b6febcb6b29b2c56ccf5f8fbc3d6fdcda93`.

Die Suite erzeugte nur neutrale PCM-Fixtures, keine NW-Payloads. Ihre sechs
Analysen/NJ-Aufrufe sind nicht mit einer separaten NW-Materialisierung zu
verwechseln. Keine Memory-, Feld-, Kontext- oder Runtimeintegration.
Der neutrale Haupteinstieg nutzte temporaere synthetische Bindungen und
setzte sein Gate im `finally` wieder auf `False`.

## Verbleibende Grenzen

Die kausale Freigabe wird durch den kontrollierten Aufrufpfad abgesichert,
nicht durch einen alleinstehenden Abschlussdigest. Der Offline-Verifikator
rechnet gespeicherte Roh-/Halbwerte, Prognosen, Fehler und Lernketten nach;
er wiederholt weder PCM/FFT/NJ noch beweist er historische CPU-Reihenfolge.
Der reine Updatehelfer verlangt ein beobachtetes Dreierfenster; dass es
bereits beobachtet wurde, erzwingt der private Controller. Dies ist keine
Sandbox gegen beliebigen feindlichen Python-Hostcode.

Noch offen sind Rezeptorgueltigkeit und Lern-/Transfernutzen der 26
versiegelten NW-Fenster. Kein erwarteter Koeffizient wurde aus deren Rezepten
berechnet oder uebernommen. Die gemeinsame Dynamikklasse waere auch bei
spaeterem Erfolg nur ein begrenzter Transfer, keine Quellenidentitaet,
Objektbindung oder allgemeines Sequenzlernen. ME/MI bleiben gesperrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser neutralen
Update-, Zukunfts- und Einfrierdeckung und danach einer separaten Entscheidung
ueber den einmaligen realen NW-Lern-/Transferlauf weiter.
