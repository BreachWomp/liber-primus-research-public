# Phase 29: A known control and its incorrect optimum

**This is not a newly decrypted LP page.** It is a deliberately encrypted
Emerson control whose truth was known beforehand. Search receives ciphertext
and boundaries only. Source: chapter XII, paragraph 1, character range
[395179,396102] in the unchanged UTF-8-decoded source file.

The first block is the correct text; the second is the highest-scoring wrong
output. GP spellings and source word boundaries are preserved. Accuracy is
65/67 runes. Truth scores -2.421091301; the wrong candidate scores -2.321066389
(higher is better). A P/Y swap produces TRAPS instead of TRAYS and YANS instead
of PANS. TRAPS occurs once in training; the other three words do not. Its reward
outweighs the other error. This is a demonstrated scoring failure. The exact
reversible mapping is in `result.top.mapping_cipher_to_plain` in the result.

## Preserved output block 1

```text
GIUE / TO / BARROWS / TRAYS / AND / PANS / GRACE / AND / GLIMMER / OF / ROMANCE / BRNG / THE / MOONLIGHT / INTO
```

## Preserved output block 2

```text
GIUE / TO / BARROWS / TRAPS / AND / YANS / GRACE / AND / GLIMMER / OF / ROMANCE / BRNG / THE / MOONLIGHT / INTO
```

## Evidence

- [E081-control-5-acb6c1a444ff.json](../../results/E081-control-5-acb6c1a444ff.json)
- Recorded result SHA-256: `5694b5a39177ad169796a4aa1bb1a57d2029da95a7bef44bfe2a84ac41503acc`
- [Original frozen appendix](../../reports/phase29_control_comparison.md)
- [English phase report](phase29.md)
