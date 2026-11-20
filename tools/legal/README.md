# Legal pages generator

`msa.html`, `msa-v<version>.html`, `order-form.html` and `editorial-policy.html`
are generated from the bilingual DOCX files supplied by the lawyer.
Do not edit those HTML files by hand; regenerate them.

## Publishing a new version of the MSA or Order Form

1. Keep the lawyer's DOCX files outside the repo (e.g. `../legal_sources/`);
   only PDFs are published. Export each DOCX to PDF (Pages does it headlessly:
   `osascript -e 'tell application "Pages" to export (open POSIX file "<docx>") to POSIX file "<pdf>" as PDF'`,
   Word's AppleScript export hangs) and put the PDFs into `assets/docs/` with the
   version in the name, e.g. `moderAItor_MSA_v1.1_AM-EN.pdf`.
2. Extract the tables from the DOCX files:
   ```
   python3 -I tools/legal/docx_rows.py ../legal_sources/moderAItor_MSA_v1.1_AM-EN.docx tools/legal/data/msa.json
   python3 -I tools/legal/docx_rows.py ../legal_sources/moderAItor_Order_Form_v1.1_AM-EN.docx tools/legal/data/order.json
   ```
3. In `tools/legal/build_legal.py` update `VERSION`, `EFFECTIVE_EN`, `EFFECTIVE_HY`,
   `MSA_PDF`, `ORDER_PDF`, and add a row for the previous version to the
   version-history tables (keep its `msa-v<old>.html` file in the repo: that is
   the permanent link to the old edition).
4. Run `python3 -I tools/legal/build_legal.py` from the repo root.
5. Update `sitemap.xml` `lastmod` and commit.

Cross-references ("Privacy Policy", "Appendix 3", "Clause 1.6", "Section 16",
and their Armenian forms) are turned into links automatically; every numbered
clause gets an anchor `#clause-1-6`, every section `#section-16`.

Appendix 5 (`editorial-policy.html`) is generated from `data/editorial-policy.txt`,
which is the text of the lawyer's PDF extracted with
`pdftotext assets/docs/moderAItor_Editorial_Policy_v1.0_AM.pdf tools/legal/data/editorial-policy.txt`
(no `-layout`). `editorial_policy.py` turns it into headings, clauses, lists and
the glossary; the cover-page credits are written by hand in `CREDITS` there.
For a new version: replace the PDF, re-extract the text, update `POLICY_PDF`
and the version-history row in `build_legal.py`, regenerate.

Appendices 2–4 (`terms.html`, `privacy.html`, `data-deletion.html`) are
ordinary hand-edited pages; they carry a `legal-meta` header and a
version-history table that must be updated by hand on each change.
