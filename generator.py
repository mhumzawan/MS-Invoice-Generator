import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_invoice_pdf(meta_data, line_items, output_filename="invoice.pdf"):
    # Target letter size with small margins to maximize printable space
    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Typographic Styles
    title_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=30, alignment=1
    )
    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1
    )
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=11
    )
    cell_style_bold = ParagraphStyle(
        'CellStyleBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=11
    )

    # 1. Header Section (Matching company block)
    story.append(Paragraph("<b>BILL/SALES-TAX INVOICE</b>", title_style))
    story.append(Paragraph("<b>MANAGEMENT SERVICES</b>", ParagraphStyle('Sub', parent=title_style, fontSize=20)))
    story.append(Paragraph("38- Ghazali Flats GOR-IV Model Town Extension Lahore.", ParagraphStyle('Addr', parent=cell_style, alignment=1)))
    story.append(Paragraph("Sales-Tax Registration No. 03-00-XXXX-XXX-XX", ParagraphStyle('STRN', parent=cell_style, alignment=1)))
    story.append(Spacer(1, 20))

    # 2. Meta Metadata Grid (Split layout)
    meta_data_left = [
        [Paragraph(f"<b>Buyer's Name:</b> {meta_data.get('buyer_name', '')}", cell_style)],
        [Paragraph(f"<b>PO Number:</b> {meta_data.get('po_number', '')}", cell_style)],
        [Paragraph(f"<b>Phone No:</b> {meta_data.get('phone', '')}", cell_style)]
    ]
    meta_data_right = [
        [Paragraph(f"<b>Bill Number:</b> {meta_data.get('bill_number', '')}", cell_style)],
        [Paragraph(f"<b>Date:</b> {meta_data.get('date', '')}", cell_style)],
        [Paragraph("<b>Terms of Sale:</b> Cash / Credit", cell_style)]
    ]
    
    meta_table = Table([
        [Table(meta_data_left, colWidths=[260]), Table(meta_data_right, colWidths=[260])]
    ], colWidths=[270, 270])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 3. Main Operational Printing Table Elements
    # Table Headings matching exactly your columns
    table_data = [[
        Paragraph("Qty.", header_style),
        Paragraph("DESCRIPTION", header_style),
        Paragraph("Price", header_style),
        Paragraph("Value Exclusive Sales-Tax", header_style),
        Paragraph("Rate of S.T.", header_style),
        Paragraph("Total Sales-Tax Payable", header_style),
        Paragraph("Value Including Sales-Tax", header_style)
    ]]

    grand_exclusive = 0.0
    grand_tax = 0.0
    grand_inclusive = 0.0

    # Populate Rows dynamically while tracking structural sums
    for item in line_items:
        qty = float(item.get('qty', 0) or 0)
        price = float(item.get('price', 0) or 0)
        st_rate = float(item.get('st_rate', 18) or 0) # default to your 18% pattern
        
        # Exact arithmetic formulas matching physical printing logic
        val_exclusive = qty * price
        tax_payable = val_exclusive * (st_rate / 100.0)
        val_inclusive = val_exclusive + tax_payable

        grand_exclusive += val_exclusive
        grand_tax += tax_payable
        grand_inclusive += val_inclusive

        table_data.append([
            Paragraph(f"{int(qty) if qty.is_integer() else qty}", cell_style),
            Paragraph(item.get('description', ''), cell_style),
            Paragraph(f"{price:,.2f}", cell_style),
            Paragraph(f"{val_exclusive:,.2f}", cell_style),
            Paragraph(f"{int(st_rate)}%", cell_style),
            Paragraph(f"{tax_payable:,.2f}", cell_style),
            Paragraph(f"{val_inclusive:,.2f}", cell_style)
        ])

    # Append the Summary/Total Row at the base of the table matrix
    table_data.append([
        Paragraph("<b>TOTAL:</b>", cell_style_bold),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph(f"<b>{grand_exclusive:,.2f}</b>", cell_style_bold),
        Paragraph("", cell_style),
        Paragraph(f"<b>{grand_tax:,.2f}</b>", cell_style_bold),
        Paragraph(f"<b>{grand_inclusive:,.2f}</b>", cell_style_bold)
    ])

    # Column mapping widths tailored to 540 max text boundary width
    col_widths = [45, 175, 45, 75, 40, 80, 80]
    
    invoice_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 30))

    # 4. Authentication/Signature Blocks
    sig_data = [
        [Paragraph(f"<b>Net Tax Inclusive Value:</b> Rs. {grand_inclusive:,.2f}", cell_style_bold), 
         Paragraph("<b>Signature:</b> ____________________", ParagraphStyle('Sig', parent=cell_style, alignment=2))]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    story.append(sig_table)

    # Compile structure to PDF
    doc.build(story)
    return output_filename
