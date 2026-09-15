from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import mm

from .qr import generate_qr_png_bytes


def generate_invoice_pdf(invoice):
    """Invoice ka PDF banata hai — restaurant bill jaisa design, GST breakup + QR code ke saath."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=invoice.invoice_number,
                             leftMargin=50, rightMargin=50, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    business_name = getattr(settings, "BUSINESS_NAME", "RewardsApp")
    business_tagline = getattr(settings, "BUSINESS_TAGLINE", "")
    business_address = getattr(settings, "BUSINESS_ADDRESS", "")
    business_gstin = getattr(settings, "BUSINESS_GSTIN", "N/A")
    business_phone = getattr(settings, "BUSINESS_PHONE", "")
    business_food_tagline = getattr(settings, "BUSINESS_FOOD_TAGLINE", "")

    title_style = ParagraphStyle("BizTitle", parent=styles["Title"], fontSize=26, leading=28)
    tagline_style = ParagraphStyle("Tagline", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    address_style = ParagraphStyle("Address", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    center_style = ParagraphStyle("Center", parent=styles["Normal"], alignment=TA_CENTER)
    qr_caption_style = ParagraphStyle("QRCaption", parent=styles["Normal"], fontSize=7, alignment=TA_CENTER)

    # Header: business name + tagline + address (left), QR code (right)
    qr_bytes = generate_qr_png_bytes()
    qr_img = Image(BytesIO(qr_bytes), width=28 * mm, height=28 * mm)

    header_left = [Paragraph(f"<b>{business_name}</b>", title_style)]
    if business_tagline:
        header_left.append(Paragraph(f"— {business_tagline} —", tagline_style))
    if business_address:
        header_left.append(Paragraph(business_address, address_style))

    header_table = Table([[header_left, [qr_img, Paragraph("SCAN TO FOLLOW US", qr_caption_style)]]],
                          colWidths=[350, 120])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>GSTIN:</b> {business_gstin} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Invoice #:</b> {invoice.invoice_number}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    order = invoice.order
    elements.append(Paragraph(f"<b>Table No:</b> {order.table_number or '—'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Order:</b> {order.bill_number}", styles["Normal"]))
    elements.append(Spacer(1, 10))
    day_date_time = [
        [f"DAY\n{invoice.created_at.strftime('%A').upper()}",
         f"DATE\n{invoice.created_at.strftime('%d %b %Y').upper()}",
         f"TIME\n{invoice.created_at.strftime('%I:%M %p')}"]
    ]
    ddt_table = Table(day_date_time, colWidths=[160, 160, 150])
    ddt_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(ddt_table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Customer: {order.user.get_full_name() or order.user.username} ({order.user.email})", styles["Normal"]))
    elements.append(Spacer(1, 10))

    item_style = ParagraphStyle("ItemCell", parent=styles["Normal"], fontSize=9)
    addon_style = ParagraphStyle("AddonCell", parent=styles["Normal"], fontSize=7, textColor=colors.grey)

    data = [["ITEM", "QTY", "PRICE", "AMOUNT"]]
    for item in order.items.all():
        if item.addons_summary:
            item_cell = [Paragraph(item.item_name, item_style), Paragraph(item.addons_summary, addon_style)]
        else:
            item_cell = Paragraph(item.item_name, item_style)
        data.append([item_cell, str(item.quantity), f"Rs. {item.price}", f"Rs. {item.subtotal}"])

    table = Table(data, colWidths=[220, 60, 90, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1512")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    summary_data = [
        ["Subtotal", f"Rs. {invoice.subtotal}"],
        [f"CGST ({invoice.cgst_rate}%)", f"Rs. {invoice.cgst_amount}"],
        [f"SGST ({invoice.sgst_rate}%)", f"Rs. {invoice.sgst_amount}"],
    ]
    summary_table = Table(summary_data, colWidths=[370, 90])
    summary_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 6))

    total_table = Table([["TOTAL", f"Rs. {invoice.total_amount}"]], colWidths=[370, 90])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1a1512")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 14))

    # Payment method / cash breakdown (agar payment ho chuka hai)
    order = invoice.order
    payment_detail = getattr(order, "payment_detail", None)
    if payment_detail:
        pay_style = ParagraphStyle("Pay", parent=styles["Normal"], fontSize=9)
        lines = [f"<b>Payment Method:</b> {payment_detail.get_method_display()}"]
        if payment_detail.method == "cash":
            lines.append(f"Cash Received: Rs. {payment_detail.cash_received} ({payment_detail.cash_received_breakdown})")
            if payment_detail.change_given:
                lines.append(f"Change Given: Rs. {payment_detail.change_given} ({payment_detail.change_given_breakdown})")
        pay_table = Table([[Paragraph("<br/>".join(lines), pay_style)]], colWidths=[460])
        pay_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(pay_table)

    elements.append(Spacer(1, 20))

    if business_food_tagline:
        elements.append(Paragraph(business_food_tagline, center_style))
    elements.append(Paragraph("Thank you for visiting us!", center_style))
    if business_phone:
        elements.append(Paragraph(f"<b>{business_phone}</b>", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
