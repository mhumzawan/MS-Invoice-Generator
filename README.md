# MS Invoice Generator

Sales-tax invoice generator for **Management Services**. It's a static web app hosted on Netlify, so it never goes to sleep.

- **Typing mode**: fill in the details and line items; the PDF is built in the browser (`public/invoice-pdf.js`, jsPDF).
- **Voice mode**: record a dictation; `netlify/functions/parse-voice.mjs` sends it to Gemini, then the form is filled in so you can check it before downloading.

## Deploy on Netlify
1. Netlify → **Add new site → Import an existing project** → GitHub → `MS-Invoice-Generator`.
2. Build settings are read from `netlify.toml` (publish `public`, no build command).
3. **Site configuration → Environment variables**:
   - `GEMINI_API_KEY`: required for voice mode.
   - `APP_PIN`: optional. If set, voice mode asks for this PIN once per device, so strangers can't use up your Gemini quota.
   - `GEMINI_MODEL`: optional, defaults to `gemini-2.5-flash`.
4. Deploy. Changes to environment variables need a redeploy before they take effect.

## Layout
```
public/                 static site (index.html, invoice-pdf.js, Signature.png, vendor/)
netlify/functions/      parse-voice.mjs → POST /api/parse-voice
app.py, generator.py    legacy Streamlit version (kept until Netlify is live)
```
