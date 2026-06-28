import streamlit as st
import datetime
from generator import generate_invoice_pdf


# Initialize application settings and look-and-feel preferences
st.set_page_config(page_title="Accessible Invoice Generator", layout="wide")
st.title("🖨️ Printing Business Invoice Hub")

# Persistent Session State Initializations
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'rows' not in st.session_state:
    st.session_state.rows = [{'qty': 1.0, 'desc': '', 'price': 0.0, 'st': 18.0}]

# Structural Mode Selectors
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("⌨️ Create Invoice by Typing", use_container_width=True):
        st.session_state.mode = 'typing'
with col_btn2:
    if st.button("🎙️ Create Invoice by Voice", use_container_width=True):
        st.session_state.mode = 'voice'

st.divider()

# --- OPTION A: MANUAL STRUCTURED TYPING INTERFACE ---
if st.session_state.mode == 'typing':
    st.subheader("📋 Document Metadata Entries")
    
    # Primary Meta Row Elements
    c1, c2, c3 = st.columns(3)
    with c1:
        invoice_date = st.date_input("Date", datetime.date.today())
        buyer_name = st.text_input("Buyer's Name", placeholder="e.g., Zubaida Associates")
    with c2:
        bill_number = st.text_input("Bill Number", placeholder="e.g., 25-26-116")
        po_number = st.text_input("PO Number")
    with c3:
        phone_number = st.text_input("Phone Number")

    st.markdown("### 📦 Line Items & Job Allocations")
    
    updated_rows = []
    # Dynamic Form Input Multi-row Rendering Loops
    for idx, row in enumerate(st.session_state.rows):
        st.markdown(f"**Item Row #{idx + 1}**")
        cols = st.columns([1, 3, 1.5, 1, 1.5, 1.5, 1.5])
        
        with cols[0]:
            qty = st.number_input("Qty", min_value=0.0, value=float(row['qty']), step=1.0, key=f"qty_{idx}")
        with cols[1]:
            desc = st.text_input("Description", value=row['desc'], placeholder="Job printing specifications...", key=f"desc_{idx}")
        with cols[2]:
            price = st.number_input("Rate / Unit", min_value=0.0, value=float(row['price']), step=10.0, key=f"price_{idx}")
        with cols[3]:
            st_rate = st.number_input("S.T. %", min_value=0.0, max_value=100.0, value=float(row['st']), step=1.0, key=f"st_{idx}")
        
        # Real-time Background Math Aggregations 
        val_excl = qty * price
        tax_val = val_excl * (st_rate / 100.0)
        val_incl = val_excl + tax_val

        # Display Computed Values cleanly
        with cols[4]:
            st.text_input("Value Excl. S.T", value=f"{val_excl:,.2f}", disabled=True, key=f"excl_disp_{idx}")
        with cols[5]:
            st.text_input("Sales Tax Amount", value=f"{tax_val:,.2f}", disabled=True, key=f"tax_disp_{idx}")
        with cols[6]:
            st.text_input("Total Inc. Tax", value=f"{val_incl:,.2f}", disabled=True, key=f"incl_disp_{idx}")
            
        # Store mutations safely back to session state structure
        updated_rows.append({'qty': qty, 'desc': desc, 'price': price, 'st': st_rate})
    
    st.session_state.rows = updated_rows

    # Append dynamic table row mutations via session array extensions
    if st.button("➕ Add Item Row"):
        st.session_state.rows.append({'qty': 1.0, 'desc': '', 'price': 0.0, 'st': 18.0})
        st.rerun()

    st.divider()

    # Document Trigger compilation sequence
    if st.button("🔥 Generate and Download Invoice", type="primary", use_container_width=True):
        meta = {
            'date': invoice_date.strftime("%d-%m-%Y"),
            'buyer_name': buyer_name,
            'bill_number': bill_number,
            'po_number': po_number,
            'phone': phone_number
        }
        
        # Compile raw UI rows into schema payloads
        lines = []
        for r in st.session_state.rows:
            lines.append({
                'qty': r['qty'],
                'description': r['desc'],
                'price': r['price'],
                'st_rate': r['st']
            })
            
        pdf_path = generate_invoice_pdf(meta, lines)
        
        # Hand off compilation file binary directly via safe stream buffers
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Invoice PDF",
                data=f,
                file_name=f"Bill_{bill_number if bill_number else 'Draft'}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- OPTION B: AUDIO INGESTION SYSTEM ---
elif st.session_state.mode == 'voice':
    st.subheader("🎙️ Voice Automated Ledger Engine")
    st.info("Dictate invoice details naturally (e.g., 'Create a bill for Ali Raza, phone 03001234567, job is 500 brochures at 15 rupees each with 18 percent sales tax').")
    
    audio_file = st.file_uploader("Upload or Record Audio Log File", type=["wav", "mp3", "m4a"])
    
    if audio_file:
        # Crucial fix: Reset file reader pointer to the beginning before reading bytes
        audio_file.seek(0)
        audio_bytes = audio_file.read()
        st.success("Audio data packet ingested successfully.")
        
        if st.button("✨ Process Voice & Generate Invoice", type="primary", use_container_width=True):
            with st.spinner("Analyzing audio context and generating document layout..."):
                try:
                    import requests
                    import base64
                    import json
                    
                    # Force-remove any hidden spaces, line breaks, or quotation marks from the secret string
                    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().replace('"', '').replace("'", "")
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    
                    # Target endpoint matching official Gemini 2.5 REST guidelines
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                    
                    # Refined payload structure ensuring clean multipart block delivery
                    payload = {
                        "contents": [{
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": audio_file.type,
                                        "data": audio_b64
                                    }
                                },
                                {
                                    "text": (
                                        "Analyze this spoken invoice dictation. Extract details into a JSON object matching this structure: "
                                        "{"
                                        "  \"buyer_name\": \"string\","
                                        "  \"bill_number\": \"string\","
                                        "  \"po_number\": \"string\","
                                        "  \"phone\": \"string\","
                                        "  \"line_items\": [{\"qty\": 1.0, \"description\": \"string\", \"price\": 0.0, \"st_rate\": 18.0}]"
                                        "}"
                                        "Respond strictly with valid JSON. Do not include markdown code block formatting."
                                    )
                                }
                            ]
                        }]
                    }
                    
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(url, headers=headers, json=payload)
                    response_json = response.json()
                    
                    # Safe check: Catch API errors (invalid key, bad file type, etc.) before digging into candidates
                    if "error" in response_json:
                        st.error(f"Gemini API Error: {response_json['error'].get('message', 'Unknown error context')}")
                        st.stop()
                    
                    # Extract the raw text safely
                    try:
                        raw_text = response_json['candidates'][0]['content']['parts'][0]['text']
                    except KeyError:
                        st.error("The model couldn't process the audio correctly. Try speaking more clearly or using a standard WAV/MP3 format.")
                        st.write("API Response for debugging:", response_json)
                        st.stop()
                        
                    # Clean up any residual json wrapping characters if present
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.replace("```json", "", 1).rstrip("```")
                    elif raw_text.startswith("```"):
                        raw_text = raw_text.replace("```", "", 1).rstrip("```")
                        
                    invoice_data = json.loads(raw_text.strip())
                    
                    # Format layout meta variables
                    meta = {
                        'date': datetime.date.today().strftime("%d-%m-%Y"),
                        'buyer_name': invoice_data.get('buyer_name', 'Voice Order'),
                        'bill_number': invoice_data.get('bill_number', 'Voice-Draft'),
                        'po_number': invoice_data.get('po_number', ''),
                        'phone': invoice_data.get('phone', '')
                    }
                    
                    # Compile extracted rows
                    lines = []
                    for item in invoice_data.get('line_items', []):
                        lines.append({
                            'qty': float(item.get('qty', 1)),
                            'description': item.get('description', 'Printing Job'),
                            'price': float(item.get('price', 0)),
                            'st_rate': float(item.get('st_rate', 18))
                        })
                    
                    if not lines:
                        lines = [{'qty': 1.0, 'description': 'Voice Dictated Printing Job', 'price': 0.0, 'st_rate': 18.0}]
                    
                    # Compile the PDF template
                    pdf_path = generate_invoice_pdf(meta, lines)
                    
                    st.balloons()
                    st.success("Invoice generated perfectly from voice dictation!")
                    st.markdown(f"**Extracted Buyer:** {meta['buyer_name']} | **Total Items processed:** {len(lines)}")
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Voice Generated Invoice PDF",
                            data=f,
                            file_name=f"Voice_Bill_{meta['bill_number']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"An error occurred while processing the audio: {str(e)}")