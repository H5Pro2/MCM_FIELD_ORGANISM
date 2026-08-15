# S1-HC: Lauf-197-Ausfuehrungseinstieg

S1-HC bindet die ausdruecklich autorisierte Einmalausfuehrung an genau eine
S1-GU-Aufrufstelle. S1-GS ist die injizierte reale Einzelbatch-Transition und
S1-HB der reale terminale Outputabschluss. Der Umfang bleibt auf sechs Arme,
2.800 Feldschritte und 660 Supports begrenzt.

Der Einstieg schreibt keine Ergebnis-, Lock- oder Attemptdatei. Er gibt nach
einer vollstaendigen atomaren Rueckgabe nur eine JSON-Zusammenfassung auf der
Konsole aus. Enthalten sind Gesamtbilanz, Digests, sechs armweise Rohmetriken
und die AB/BA-Linf-Differenzen pro Verfeinerung. Es gibt keine Retry-Schleife
und keine Memoryentscheidung.

Da Lauf 196 der letzte nachweislich nummerierte ausgefuehrte Forschungslauf
ist und die fruehere Reservierung von 197 nie ausgefuehrt wurde, erhaelt diese
Untersuchung unmittelbar vor ihrer Ausfuehrung die Laufnummer 197.

Nachtrag: Der direkte Dateistart brach vor dem Import der Fixturequelle und
vor der S1-GU-Aufrufstelle technisch ab. Lauf 197 fuehrte null Feldschritte
aus und ist gegen Retry versiegelt. Siehe
`S1HD_LAUF_197_TECHNISCHER_VORSTARTABBRUCH.md`.
