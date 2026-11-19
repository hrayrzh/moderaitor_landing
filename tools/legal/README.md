# Legal pages generator

`msa.html`, `msa-v<version>.html`, `order-form.html` and `editorial-policy.html`
are generated from the bilingual DOCX files supplied by the lawyer.
Do not edit those HTML files by hand; regenerate them.

## Publishing a new version of the MSA or Order Form

1. Put the new DOCX files into `assets/docs/` with the version in the name,
   e.g. `moderAItor_MSA_v1.1_AM-EN.docx`.
2. Extract the tables:
   ```
   python3 -I tools/legal/docx_rows.py assets/docs/moderAItor_MSA_v1.1_AM-EN.docx tools/legal/data/msa.json
   python3 -I tools/legal/docx_rows.py assets/docs/moderAItor_Order_Form_v1.1_AM-EN.docx tools/legal/data/order.json
   ```
3. In `tools/legal/build_legal.py` update `VERSION`, `EFFECTIVE_EN`, `EFFECTIVE_HY`,
   `MSA_DOCX`, `ORDER_DOCX`, and add a row for the previous version to the
   version-history tables (keep its `msa-v<old>.html` file in the repo: that is
   the permanent link to the old edition).
4. Run `python3 -I tools/legal/build_legal.py` from the repo root.
5. Update `sitemap.xml` `lastmod` and commit.

Cross-references ("Privacy Policy", "Appendix 3", "Clause 1.6", "Section 16",
and their Armenian forms) are turned into links automatically; every numbered
clause gets an anchor `#clause-1-6`, every section `#section-16`.

Appendices 2–4 (`terms.html`, `privacy.html`, `data-deletion.html`) are
ordinary hand-edited pages; they carry a `legal-meta` header and a
version-history table that must be updated by hand on each change.
