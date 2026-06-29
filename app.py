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

# --- OPTION B: AUDIO INGESTION SYSTEM (LIVE MIC RECORDER) ---
elif st.session_state.mode == 'voice':
    st.subheader("🎙️ Live Voice Automated Ledger Engine")
    st.info("Click 'Start recording', dictate invoice details naturally, and click 'Stop' when you are finished.")
    
    # 1. Import and render the stable mic recorder component
    from streamlit_mic_recorder import mic_recorder
    
    # This renders a clean interactive UI widget with a live microphone indicator
    audio_packet = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="🛑 Stop & Process Invoice",
        just_once=False,
        use_container_width=True,
        key='invoice_mic'
    )
    
    # Check if a valid audio recording stream was stopped and captured
    if audio_packet and 'bytes' in audio_packet:
        st.success("Voice recording captured successfully!")
        
        with st.spinner("Analyzing vocal track with Gemini 2.5 Flash..."):
            try:
                import google.generativeai as genai
                import json
                import datetime
                
                # Extract raw audio data bytes straight from the widget memory map
                audio_bytes = audio_packet['bytes']
                
                # Setup API credentials securely
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip().replace('"', '').replace("'", "")
                genai.configure(api_key=api_key)
                
                # Format into a secure data blob matching the widget's native audio stream format
                audio_blob = {
                    "mime_type": "audio/wav",
                    "data": audio_bytes
                }
                
                prompt_text = (
                    "Listen carefully to this spoken invoice dictation. Extract the billing information and "
                    "return a strictly structured JSON object matching this schema:\n\n"
                    "{\n"
                    "  \"buyer_name\": \"string\",\n"
                    "  \"bill_number\": \"string\",\n"
                    "  \"po_number\": \"string\",\n"
                    "  \"phone\": \"string\",\n"
                    "  \"line_items\": [\n"
                    "    {\"qty\": 1.0, \"description\": \"string\", \"price\": 0.0, \"st_rate\": 18.0}\n"
                    "  ]\n"
                    "}\n\n"
                    "Rules:\n"
                    "1. Respond ONLY with valid, parsable raw JSON. Do not include markdown formatting or ```json blocks.\n"
                    "2. Carefully capture South Asian names and phone numbers spoken in the track.\n"
                    "3. If details like Bill Number or PO are missing, leave them blank or create a short draft placeholder."
                )
                
                # Feed raw multi-modal layout directly to Gemini 2.5 Flash
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content([audio_blob, prompt_text])
                
                raw_text = response.text.strip()
                
                # Sanitize structural code blocks if present
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "", 1).rstrip("```")
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "", 1).rstrip("```")
                
                invoice_data = json.loads(raw_text.strip())
                
                # Map the AI-extracted fields directly to your document template
                meta = {
                    'date': datetime.date.today().strftime("%d-%m-%Y"),
                    'buyer_name': invoice_data.get('buyer_name', 'Voice Order Customer'),
                    'bill_number': invoice_data.get('bill_number', 'LIVE-MIC-DRAFT'),
                    'po_number': invoice_data.get('po_number', ''),
                    'phone': invoice_data.get('phone', '')
                }
                
                lines = []
                for item in invoice_data.get('line_items', []):
                    lines.append({
                        'qty': float(item.get('qty', 1)),
                        'description': item.get('description', 'Printing Job Order'),
                        'price': float(item.get('price', 0)),
                        'st_rate': float(item.get('st_rate', 18))
                    })
                
                if not lines:
                    lines = [{'qty': 1.0, 'description': 'Voice Dictated Printing Job', 'price': 0.0, 'st_rate': 18.0}]
                
                # Pass compiled matrices to your ReportLab PDF module
                pdf_path = generate_invoice_pdf(meta, lines)
                
                st.balloons()
                st.success("Invoice generated perfectly from live audio mic layout!")
                st.markdown(f"**Extracted Buyer Name:** {meta['buyer_name']} | **Total Calculated Lines:** {len(lines)}")
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Voice Generated Invoice PDF",
                        data=f,
                        file_name=f"Voice_Bill_{meta['bill_number']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"An error occurred while compiling your layout: {str(e)}")