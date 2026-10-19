# S2-SP: PPB-Readout-Anschlussqualifikation

Qualifikations-ID: `S2SP-PPB-READOUT-QUAL-20260919-01`.

Ein fokussierter neutraler Aufruf von
`python -B -m unittest tests.test_s2sp_ppb_readout_evidence -v` bestand mit
`2/2`.

- Bei einer konsolidierten Formation werden visueller PPB-Readout, Ereignis,
  Slot-ID, Eingangsdigest, Vor-/Nachzustandsdigest und Readout-Digest durch
  den privaten S2-SP-Ergebnisweg geführt.
- Bei einer nicht konsolidierbaren Formation bleibt der Readout leer; es wird
  kein PPB-Ereignis erfunden.

Dies qualifiziert nur die zusätzliche Nachweisführung. Die konkrete
22-Ereignis-V2-Geschichte ist nicht qualifiziert und nicht ausgeführt.
