// Netlify Function: receives a recorded dictation (base64 audio) and asks Gemini
// to extract invoice fields. Keeps GEMINI_API_KEY server-side.
// Set GEMINI_API_KEY (and optionally APP_PIN) in Netlify → Site configuration → Environment variables.

const PROMPT =
  'Listen carefully to this spoken invoice dictation. Extract the billing information and ' +
  'return a strictly structured JSON object matching this schema:\n\n' +
  '{\n' +
  '  "buyer_name": "string",\n' +
  '  "bill_number": "string",\n' +
  '  "po_number": "string",\n' +
  '  "phone": "string",\n' +
  '  "line_items": [\n' +
  '    {"qty": 1.0, "description": "string", "price": 0.0, "st_rate": 18.0}\n' +
  '  ]\n' +
  '}\n\n' +
  'Rules:\n' +
  '1. Respond ONLY with valid, parsable raw JSON. Do not include markdown formatting or ```json blocks.\n' +
  '2. Carefully capture South Asian names and phone numbers spoken in the track.\n' +
  '3. If details like Bill Number or PO are missing, leave them blank or create a short draft placeholder.';

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export default async (req) => {
  if (req.method !== 'POST') return json(405, { error: 'Use POST' });

  const apiKey = (process.env.GEMINI_API_KEY || '').trim().replace(/["']/g, '');
  if (!apiKey) return json(500, { error: 'GEMINI_API_KEY is not set on Netlify.' });

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: 'Invalid JSON body' });
  }

  const pin = process.env.APP_PIN;
  if (pin && payload.pin !== pin) return json(401, { error: 'Wrong PIN' });

  const { audio, mimeType } = payload;
  if (!audio) return json(400, { error: 'No audio received' });

  const model = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ inline_data: { mime_type: mimeType || 'audio/wav', data: audio } }, { text: PROMPT }] }],
      generationConfig: { responseMimeType: 'application/json', temperature: 0.1 }
    })
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) return json(502, { error: data?.error?.message || `Gemini error ${res.status}` });

  let text = (data?.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('').trim();
  text = text.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();

  try {
    return json(200, JSON.parse(text));
  } catch {
    return json(502, { error: 'Could not read Gemini response', raw: text.slice(0, 500) });
  }
};

export const config = { path: '/api/parse-voice' };
