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

# --- OPTION B: AUDIO INGESTION SYSTEM (TRUE OFFLINE ENGINE) ---
elif st.session_state.mode == 'voice':
    st.subheader("🎙️ Voice Automated Ledger Engine (True Offline)")
    st.info("Upload your audio dictation. The local Vosk engine will process everything directly on the server without any external API calls.")
    
    audio_file = st.file_uploader("Upload or Record Audio Log File", type=["wav", "mp3", "m4a"])
    
    if audio_file:
        st.success("Audio data packet ingested successfully.")
        
        if st.button("✨ Process Voice & Generate Invoice", type="primary", use_container_width=True):
            with st.spinner("Processing audio tracks on local CPU..."):
                try:
                    from vosk import Model, KaldiRecognizer
                    from pydub import AudioSegment
                    import io
                    import re
                    import datetime
                    import json
                    import os
                    
                    # Verify model folder presence
                    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
                    if not os.path.exists(model_path):
                        st.error("Offline speech engine directory structure missing. Please ensure the 'model' folder is pushed to GitHub.")
                        st.stop()
                    
                    # 1. Standardize audio stream to Mono, 16000Hz WAV as required by local speech models
                    audio_file.seek(0)
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_file.read()))
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                    
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format="wav")
                    wav_io.seek(0)
                    
                    # Skip the 44-byte WAV header to feed raw PCM audio data directly to the recognizer
                    raw_audio_data = wav_io.read()[44:]
                    
                    # 2. Initialize the local engine
                    model = Model(model_path)
                    recognizer = KaldiRecognizer(model, 16000)
                    recognizer.SetWords(True)
                    
                    # Accept and process waveform chunk
                    recognizer.AcceptWaveform(raw_audio_data)
                    result_json = json.loads(recognizer.FinalResult())
                    transcription = result_json.get("text", "")
                    
                    if not transcription:
                        st.error("Local engine could not extract any words. Try speaking a bit slower or closer to the microphone.")
                        st.stop()
                        
                    st.markdown(f"**Transcribed Text:** *\"{transcription}\"*")
                    
                    # 3. STRUCTURED KEYWORD PARSER
                    words = transcription.lower()
                    numbers = re.findall(r'\d+', words)
                    
                    extracted_qty = 1.0
                    extracted_price = 0.0
                    extracted_buyer = "Voice Order Customer"
                    
                    if len(numbers) >= 2:
                        extracted_qty = float(numbers[0])
                        extracted_price = float(numbers[1])
                    elif len(numbers) == 1:
                        extracted_price = float(numbers[0])
                        
                    extracted_desc = transcription
                    if "for" in words:
                        parts = transcription.split("for", 1)
                        if len(parts) > 1:
                            extracted_desc = parts[1].strip()

                    # Compile metadata schema mapping blocks
                    meta = {
                        'date': datetime.date.today().strftime("%d-%m-%Y"),
                        'buyer_name': extracted_buyer,
                        'bill_number': "OFFLINE-Voice-Draft",
                        'po_number': "",
                        'phone': ""
                    }
                    
                    # Build rows list matrix
                    lines = [{
                        'qty': extracted_qty,
                        'description': extracted_desc,
                        'price': extracted_price,
                        'st_rate': 18.0  
                    }]
                    
                    # 4. Trigger template compilation module
                    pdf_path = generate_invoice_pdf(meta, lines)
                    
                    st.balloons()
                    st.success("Invoice generated successfully!")
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Voice Generated Invoice PDF",
                            data=f,
                            file_name="Voice_Bill_OfflineEngine.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"An error occurred while compiling your layout: {str(e)}")