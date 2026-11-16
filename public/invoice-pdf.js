// Builds the Management Services sales-tax invoice PDF in the browser.
// Mirrors the layout of the original ReportLab generator.py (US Letter, 36pt margins).
(function (root) {
  function fmt(n) {
    return Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function fmtQty(q) {
    return String(Number(q || 0));
  }

  function computeLines(lines) {
    let ex = 0, tax = 0, inc = 0;
    const rows = lines.map(function (it) {
      const qty = Number(it.qty) || 0;
      const price = Number(it.price) || 0;
      const st = it.st_rate === '' || it.st_rate == null ? 18 : Number(it.st_rate) || 0;
      const vEx = qty * price;
      const vTax = vEx * (st / 100);
      const vInc = vEx + vTax;
      ex += vEx; tax += vTax; inc += vInc;
      return { qty: qty, description: it.description || '', price: price, st: st, vEx: vEx, vTax: vTax, vInc: vInc };
    });
    return { rows: rows, ex: ex, tax: tax, inc: inc };
  }

  // jsPDFCtor: window.jspdf.jsPDF ; signature: { dataUrl, format } or null
  function buildInvoicePdf(jsPDFCtor, meta, lines, signature) {
    const doc = new jsPDFCtor({ unit: 'pt', format: 'letter' });
    const pageW = doc.internal.pageSize.getWidth();   // 612
    const pageH = doc.internal.pageSize.getHeight();  // 792
    const M = 36;
    const cx = pageW / 2;
    const calc = computeLines(lines);

    // 1. Header block
    let y = M;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(22);
    y += 27; doc.text('BILL/SALES-TAX INVOICE', cx, y, { align: 'center' });
    doc.setFontSize(20);
    y += 30; doc.text('MANAGEMENT SERVICES', cx, y, { align: 'center' });
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    y += 16; doc.text('38- Ghazali Flats GOR-IV Model Town Extension Lahore.', cx, y, { align: 'center' });
    y += 11; doc.text('Sales-Tax Registration No. 03-00-4817-026-73', cx, y, { align: 'center' });
    y += 38;

    // 2. Meta grid (two columns)
    const left = [["Buyer's Name:", meta.buyer_name], ['PO Number:', meta.po_number], ['Phone No:', meta.phone]];
    const right = [['Bill Number:', meta.bill_number], ['Date:', meta.date], ['Terms of Sale:', 'Cash / Credit']];
    function metaLine(x, label, value, yy) {
      doc.setFont('helvetica', 'bold');
      doc.text(label, x, yy);
      const w = doc.getTextWidth(label + ' ');
      doc.setFont('helvetica', 'normal');
      doc.text(String(value || ''), x + w, yy);
    }
    for (let i = 0; i < 3; i++) {
      metaLine(M + 12, left[i][0], left[i][1], y);
      metaLine(M + 282, right[i][0], right[i][1], y);
      y += 17;
    }
    y += 10;

    // 3. Line-item table
    const body = calc.rows.map(function (r) {
      return [fmtQty(r.qty), r.description, fmt(r.price), fmt(r.vEx), Math.trunc(r.st) + '%', fmt(r.vTax), fmt(r.vInc)];
    });
    body.push([
      { content: 'TOTAL:', styles: { fontStyle: 'bold' } }, '', '',
      { content: fmt(calc.ex), styles: { fontStyle: 'bold' } }, '',
      { content: fmt(calc.tax), styles: { fontStyle: 'bold' } },
      { content: fmt(calc.inc), styles: { fontStyle: 'bold' } }
    ]);

    const FOOTER_H = 70;
    function drawFooter() {
      const base = pageH - M; // bottom edge of the footer block
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.setTextColor(0);
      doc.text('Total Sales Tax Payable: Rs. ' + fmt(calc.tax), M + 6, base - 17);
      doc.text('Net Tax Inclusive Value: Rs. ' + fmt(calc.inc), M + 6, base - 2);
      if (signature && signature.dataUrl) {
        doc.addImage(signature.dataUrl, signature.format || 'PNG', M + 540 - 6 - 120, base - 40, 120, 40);
      } else {
        doc.setFont('helvetica', 'normal');
        doc.text('Signature: ____________________', M + 540 - 6, base - 2, { align: 'right' });
      }
    }

    doc.autoTable({
      startY: y,
      margin: { left: M, right: M, top: M, bottom: M + FOOTER_H + 10 },
      tableWidth: 540,
      head: [['Qty.', 'DESCRIPTION', 'Price', 'Value Exclusive Sales-Tax', 'Rate of S.T.', 'Total Sales-Tax Payable', 'Value Including Sales-Tax']],
      body: body,
      theme: 'grid',
      styles: { font: 'helvetica', fontSize: 9, textColor: 0, lineColor: 0, lineWidth: 0.5, cellPadding: { top: 6, bottom: 6, left: 6, right: 6 }, valign: 'middle', overflow: 'linebreak' },
      headStyles: { fillColor: [211, 211, 211], textColor: 0, fontStyle: 'bold', fontSize: 11, halign: 'center' },
      columnStyles: {
        0: { cellWidth: 45 }, 1: { cellWidth: 175 }, 2: { cellWidth: 45 }, 3: { cellWidth: 75 },
        4: { cellWidth: 40 }, 5: { cellWidth: 80 }, 6: { cellWidth: 80 }
      },
      showHead: 'everyPage',
      didDrawPage: drawFooter
    });

    return doc;
  }

  root.InvoicePdf = { buildInvoicePdf: buildInvoicePdf, computeLines: computeLines, fmt: fmt };
})(typeof window !== 'undefined' ? window : globalThis);
