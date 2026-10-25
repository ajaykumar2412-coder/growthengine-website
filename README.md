# GrowthEngine website

Light-mode landing page for coaches, creators and course sellers.

| File | What it is |
|---|---|
| `index.html` | The landing page, ready to open in a browser |
| `editor.html` | Visual editor: hover and click a section to move, duplicate, edit text, change background, hide or delete it, then download as Elementor JSON or HTML |
| `elementor/FX-LP-light-elementor-template.json` | Elementor template to import into WordPress |
| `elementor/FX-LP-dark-original.json` | The original dark template this was built from |
| `tools/` | Scripts that rebuild the files above from the original template |

## Before going live

- **Booking popup:** in the first block of the template, set `FX_FORM_URL` to a webhook (Zapier, Make, Google Apps Script) so form submissions are delivered somewhere. Without it, visitors see the thank-you message but the details are not sent. Optionally set `FX_BOOK_URL` to your calendar link.
- **KPI section:** the revenue / profit numbers are sample figures. Replace them with real results.
- **Placeholders:** replace `[Client name]`, `[Your Name]`, `[Brand name]`, `[3 years]`, the photo and the footer links.

## Rebuilding

```sh
python3 tools/build_light.py elementor/FX-LP-dark-original.json elementor/FX-LP-light-elementor-template.json index.html
python3 tools/build_editor.py elementor/FX-LP-light-elementor-template.json editor.html
```
