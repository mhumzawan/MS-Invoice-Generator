import streamlit as st
import datetime
from generator import generate_invoice_pdf

GEMINI_API_KEY = "AQ.Ab8RN6LPaDkqOk3qRDyoK9d0F7EK-GDS0A2XuYkzRh_Ia4d0jg"

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
    
    # 1. Ingest audio file
    audio_file = st.file_uploader("Upload or Record Audio Log File", type=["wav", "mp3", "m4a"])
    
    if audio_file:
        # Accessing the bytes clears the Streamlit warning completely
        audio_bytes = audio_file.read()
        st.success("Audio data packet ingested successfully.")
        
        if st.button("✨ Process Voice & Generate Invoice", type="primary", use_container_width=True):
            with st.spinner("Analyzing audio context and generating document layout..."):
                try:
                    from google import genai
                    from pydantic import BaseModel, Field
                    import json
                    
                    # Initialize GenAI client using the Streamlit secret token
                    api_key = st.secrets["GEMINI_API_KEY"]
                    client = genai.Client(api_key=api_key)
                    
                    # Define strict structure schemas for the LLM output matching your fields
                    class InvoiceLineItem(BaseModel):
                        qty: float = Field(description="Quantity of the item")
                        description: str = Field(description="Description of the printing job")
                        price: float = Field(description="Price per unit / rate")
                        st_rate: float = Field(default=18.0, description="Sales tax percentage rate")

                    class VoiceInvoiceSchema(BaseModel):
                        buyer_name: str = Field(default="", description="Name of the buyer/customer")
                        bill_number: str = Field(default="", description="Bill or invoice number mentioned")
                        po_number: str = Field(default="", description="Purchase order number if stated")
                        phone: str = Field(default="", description="Phone number if mentioned")
                        line_items: list[InvoiceLineItem] = Field(description="List of all printing jobs or items dictated")

                    # Deliver the audio file payload directly to Gemini 2.5 Flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            {
                                "mime_type": audio_file.type,
                                "data": audio_bytes
                            },
                            "Analyze this spoken invoice dictation. Extract the metadata fields and all operational line items into the structured schema. If details like Bill Number or PO number are missing, leave them blank."
                        ],
                        config=dict(
                            response_mime_type="application/json",
                            response_schema=VoiceInvoiceSchema,
                        ),
                    )
                    
                    # Parse extracted output map
                    invoice_data = json.loads(response.text)
                    
                    # Format dynamic meta mapping variables
                    meta = {
                        'date': datetime.date.today().strftime("%d-%m-%Y"),
                        'buyer_name': invoice_data.get('buyer_name', 'Voice Order'),
                        'bill_number': invoice_data.get('bill_number', 'Voice-Draft'),
                        'po_number': invoice_data.get('po_number', ''),
                        'phone': invoice_data.get('phone', '')
                    }
                    
                    # Compile the line item matrices
                    lines = []
                    for item in invoice_data.get('line_items', []):
                        lines.append({
                            'qty': item['qty'],
                            'description': item['description'],
                            'price': item['price'],
                            'st_rate': item['st_rate']
                        })
                    
                    # Fallback guard rule if no items were detected
                    if not lines:
                        lines = [{'qty': 1.0, 'description': 'Voice Dictated Printing Job', 'price': 0.0, 'st_rate': 18.0}]
                    
                    # Trigger your layout generator module directly
                    pdf_path = generate_invoice_pdf(meta, lines)
                    
                    st.balloons()
                    st.success("Invoice generated perfectly from voice dictation!")
                    
                    # Display summary verification for your father-in-law
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