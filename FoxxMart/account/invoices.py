"""Invoice snapshots and PDF rendering shared by every Foxx Mart storefront."""
from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail

from account.models import Invoice
from account.storefronts import STOREFRONTS


def notify_admin_of_order(invoice):
    """Notify the store administrator after a confirmed order is recorded."""
    send_mail(
        subject=f'New Foxx Mart order: {invoice.transaction_id or invoice.order_reference}',
        message=(
            f'Store: {invoice.store_name}\nOrder: {invoice.order_reference}\n'
            f'Customer: {invoice.user.email}\nSubtotal: R {invoice.subtotal:.2f}\n'
            f'Delivery: R {invoice.delivery_fee:.2f}\nVAT: R {invoice.vat_amount:.2f}\n'
            f'Total: R {invoice.total:.2f}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
        fail_silently=True,
    )


def create_invoice_for_order(*, user, store_slug, order):
    """Create exactly one invoice from the confirmed order's current line items."""
    storefront = STOREFRONTS[store_slug]
    line_items = getattr(order, storefront['order_items_accessor']).select_related('product').filter(product__isnull=False)
    items = []
    for item in line_items:
        quantity = item.quantity or 0
        unit_price = Decimal(item.product.price or 0)
        items.append({
            'name': item.product.name,
            'quantity': quantity,
            'unit_price': str(unit_price.quantize(Decimal('0.01'))),
            'line_total': str((unit_price * quantity).quantize(Decimal('0.01'))),
        })

    subtotal = Decimal(str(order.get_cart_total)).quantize(Decimal('0.01'))
    delivery_fee = Decimal(str(getattr(order, 'get_delivery_fee', Decimal('0.00')))).quantize(Decimal('0.01'))
    vat_amount = Decimal(str(getattr(order, 'get_vat_amount', Decimal('0.00')))).quantize(Decimal('0.01'))
    total = Decimal(str(getattr(order, 'get_total_with_vat', subtotal))).quantize(Decimal('0.01'))
    invoice, _ = Invoice.objects.update_or_create(
        user=user,
        store_slug=store_slug,
        order_reference=str(order.pk),
        defaults={
            'store_name': storefront['menu_label'],
            'transaction_id': str(order.transaction_id or ''),
            'status': str(order.status or ''),
            'subtotal': subtotal,
            'vat_amount': vat_amount,
            'delivery_fee': delivery_fee,
            'total': total,
            'items': items,
        },
    )
    return invoice


def invoice_pdf_response(invoice, *, download=False):
    """Return a polished, browser-viewable PDF from the immutable invoice snapshot."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    stream = BytesIO()
    document = SimpleDocTemplate(
        stream, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='InvoiceTitle', parent=styles['Title'], textColor=colors.HexColor('#111111'), fontSize=24, leading=30, spaceAfter=5))
    styles.add(ParagraphStyle(name='InvoiceMeta', parent=styles['BodyText'], textColor=colors.HexColor('#555555'), fontSize=9, leading=14))
    styles.add(ParagraphStyle(name='Money', parent=styles['BodyText'], alignment=TA_RIGHT))
    story = [
        Paragraph('FOXX MART', styles['Heading2']),
        Paragraph('INVOICE', styles['InvoiceTitle']),
        Paragraph(f'<b>{invoice.store_name}</b><br/>Invoice: INV-{invoice.store_slug.upper()}-{invoice.order_reference}<br/>Issued: {invoice.issued_at:%d %B %Y}<br/>Transaction: {invoice.transaction_id or "-"}<br/>Status: {invoice.status or "Confirmed"}', styles['InvoiceMeta']),
        Spacer(1, 12 * mm),
    ]
    rows = [['Item', 'Qty', 'Unit price', 'Total']]
    for item in invoice.items:
        rows.append([item['name'], str(item['quantity']), f"R {item['unit_price']}", f"R {item['line_total']}"])
    rows.append(['', '', 'Subtotal', f'R {invoice.subtotal:.2f}'])
    rows.append(['', '', 'Delivery', f'R {invoice.delivery_fee:.2f}'])
    rows.append(['', '', 'VAT (15%)', f'R {invoice.vat_amount:.2f}'])
    rows.append(['', '', 'Grand total', f'R {invoice.total:.2f}'])
    table = Table(rows, colWidths=[76 * mm, 18 * mm, 35 * mm, 35 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#171717')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -5), 0.25, colors.HexColor('#d4d4d4')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#171717')),
        ('FONTNAME', (2, -4), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([table, Spacer(1, 12 * mm), Paragraph('Thank you for shopping with Foxx Mart.', styles['InvoiceMeta'])])
    document.build(story)
    filename = f'foxx-mart-invoice-{invoice.public_id}.pdf'
    disposition = 'attachment' if download else 'inline'
    response = HttpResponse(stream.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response
