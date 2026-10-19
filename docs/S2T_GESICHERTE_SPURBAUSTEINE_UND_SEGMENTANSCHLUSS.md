# S2-T: Gesicherte Spurbausteine und minimaler Segmentanschluss

## Gesicherte Bausteine

* S2-TS: Ein geordneter Zweiframe-Hint liest eine vollständig aufgenommene
  Vierframe-Spur exakt und read-only.
* S2-TU: Abgeschlossene Spuren bleiben ownergebunden über Segmentabschlüsse
  erhalten; FIFO-Verdrängung und generationstreue Mehrdeutigkeit sind belegt.
* S2-TW: Eine vollständig exakte Wiederwahrnehmung vermeidet die zweite
  Doppelbelegung, ohne Generation oder FIFO-Alter zu ändern.

S2-TX bleibt davon getrennt: sein Record ist technisch verifiziert, aber
nicht vorab qualifiziert. Die Aktualitätsregel ist keine bevorzugte
Konfiguration.

## Minimaler Anschluss

Der kleinste nutzbare Anschluss liegt vor S2-TS: Ein bereits zugelassener
Wahrnehmungspfad übergibt eine explizit gebundene Folge aus bis zu vier
geordneten Halbprofilzuständen und danach ein Abschlussereignis. Jeder Zustand
trägt Profil, Owner, Segmentkennung und monotonen Ordinalwert; der Abschluss
trägt dieselbe Owner-/Segmentbindung. Die Quelle liefert weder Rollenlabels
noch Sollantworten an den Speicherpfad.

Die Segmentgrenze wird zunächst vom aufrufenden, vorgebundenen
Ereignismanifest geliefert. Es gibt keine automatische Segmentierungsregel,
keine Quellenerkennung und keine nachträgliche Grenzsuche. Der Anschluss
materialisiert ausschließlich den aktuellen Zustand, reicht ihn an den
bestehenden Aufnahmepuffer weiter und löst nur beim gebundenen Close die
vorhandene Spurübernahme aus. Read-only Hints bleiben ein separater Eingang.

Vor einem späteren Versuch wären Herkunft, Zeiten, Profil, vier Ordnungen und
der Close-Receipt zu binden und gegen die vorhandenen Größenlimits zu prüfen.
Das wäre eine Nutzung der bestehenden Bausteine im Wahrnehmungspfad, keine
neue Memoryregel.
