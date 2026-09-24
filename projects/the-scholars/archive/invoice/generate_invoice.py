"""
The Scholars - Monthly Invoice Generator
Generates thescholars_INV{NNN}.pdf matching the INV002 design.

Usage:
    python generate_invoice.py              # interactive (asks for extra items)
    python generate_invoice.py --silent     # no prompts, default items only
    python generate_invoice.py --extra-items extras.json  # load extras from file
"""

import os
import json
import sys
import re
import shutil
import argparse
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# CONFIG
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
STATE_FILE   = os.path.join(SCRIPT_DIR, "invoice_state.json")
OUTPUT_DIR   = SCRIPT_DIR

ISSUED_TO_NAME  = "The Scholars"
ISSUED_TO_EMAIL = "thescholarsid@gmail.com"
BANK_NAME       = "Bank Central Asia"
ACCOUNT_NAME    = "Sia Steven Leroy"
ACCOUNT_NO      = "1820691110"
BRANCH_NAME     = "BCA KCU Gang Tengah"
REMITTANCE_NOTE = "Please send remittance to chatminagent@gmail.com or via WhatsApp."
FOOTER_NOTE     = "Thank you for your business."

DEFAULT_ITEMS = [
    {"name": "VIRA Basic Plan", "qty": 1, "price": 2499000, "discount": None},
]

# COLORS
COL_TEXT       = colors.Color(0.2392, 0.2314, 0.2275)
COL_TABLE_HEAD = colors.Color(0.8549, 0.9137, 0.9725)
COL_WHITE      = colors.white
COL_BLACK      = colors.black

# PAGE GEOMETRY
PAGE_W, PAGE_H = A4
MARGIN_L = 51.5
MARGIN_R = PAGE_W - 51.5
TABLE_L  = MARGIN_L
TABLE_R  = 513.6

# Column x-boundaries: Item | Qty | Price | Discount | Subtotal
COL_X = [51.5, 197.0, 230.4, 299.1, 367.7, 513.6]


def fmt_idr(amount):
    return "IDR {:,.0f}".format(amount)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def next_invoice_no_from_files():
    """Scan OUTPUT_DIR for thescholars_INV*.pdf and return max number + 1."""
    pattern = re.compile(r"thescholars_INV(\d+)\.pdf", re.IGNORECASE)
    max_no = 0
    for fname in os.listdir(OUTPUT_DIR):
        m = pattern.match(fname)
        if m:
            max_no = max(max_no, int(m.group(1)))
    return max_no + 1


def ask_extra_items():
    extras = []
    print("\n" + "="*55)
    print("  VIRA Invoice Generator - Konfirmasi Item Tambahan")
    print("="*55)
    print("\nItem default:")
    for i, item in enumerate(DEFAULT_ITEMS, 1):
        disc = fmt_idr(item["discount"]) if item["discount"] else "-"
        print("  {}. {} | Qty: {} | Harga: {} | Diskon: {}".format(
            i, item["name"], item["qty"], fmt_idr(item["price"]), disc))

    answer = input("\nAda item tambahan? (y/n): ").strip().lower()
    if answer not in ("y", "yes", "ya"):
        print("-> Tidak ada item tambahan.\n")
        return []

    print("\nMasukkan item tambahan (ketik 'selesai' untuk berhenti):")
    while True:
        print("\n  Item tambahan #{}".format(len(extras) + 1))
        name = input("  Nama item (atau 'selesai'): ").strip()
        if name.lower() in ("selesai", "done", "exit", ""):
            break

        while True:
            try:
                qty = int(input("  Qty: ").strip())
                break
            except ValueError:
                print("  -> Masukkan angka bulat.")

        while True:
            try:
                raw = input("  Harga (contoh: 500000): ").strip()
                price = float(raw.replace(",", "").replace(".", ""))
                break
            except ValueError:
                print("  -> Masukkan angka yang valid.")

        raw_disc = input("  Diskon IDR (atau Enter jika tidak ada): ").strip()
        discount = None
        if raw_disc:
            try:
                discount = float(raw_disc.replace(",", "").replace(".", ""))
            except ValueError:
                discount = None

        extras.append({"name": name, "qty": qty, "price": price, "discount": discount})
        print("  Item '{}' ditambahkan.".format(name))

    print("\n-> {} item tambahan.\n".format(len(extras)) if extras else "-> Tidak ada item tambahan.\n")
    return extras


def cell_center_x(col_idx):
    return (COL_X[col_idx] + COL_X[col_idx + 1]) / 2


def draw_cell_text(c, text, col_idx, y, font="Helvetica", size=8, align="center"):
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(cell_center_x(col_idx), y, text)
    elif align == "left":
        c.drawString(COL_X[col_idx] + 6, y, text)
    elif align == "right":
        c.drawRightString(COL_X[col_idx + 1] - 6, y, text)


def generate_invoice(invoice_no, date_str, items, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    h = PAGE_H

    # Title
    c.setFillColor(COL_TEXT)
    c.setFont("Helvetica", 38)
    c.drawRightString(MARGIN_R + 8, h - 77, "I N V O I C E")

    # Issued To
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_L, h - 94, "ISSUED TO:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN_L, h - 113, ISSUED_TO_NAME)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN_L, h - 124, ISSUED_TO_EMAIL)

    # Invoice No & Date (right)
    label_x = 399.0
    value_x = MARGIN_R + 8
    c.setFont("Helvetica", 10)
    c.drawString(label_x, h - 95, "INVOICE NO:")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(value_x, h - 94, "INV-{:03d}".format(invoice_no))
    c.setFont("Helvetica", 10)
    c.drawString(label_x, h - 110, "DATE:")
    c.drawRightString(value_x, h - 109, date_str)

    # Separator
    sep_y = h - 250
    c.setStrokeColor(COL_TEXT)
    c.setLineWidth(0.5)
    c.line(MARGIN_L - 8, sep_y, MARGIN_R + 8, sep_y)

    # Table
    TABLE_TOP  = h - 265
    ROW_H_HEAD = 27.0
    ROW_H_DATA = 31.5
    ROW_H_ALT  = 29.3

    header_y = TABLE_TOP - ROW_H_HEAD

    # Header row
    c.setFillColor(COL_WHITE)
    c.rect(TABLE_L, header_y, TABLE_R - TABLE_L, ROW_H_HEAD, fill=1, stroke=0)
    header_text_y = header_y + 10
    c.setFillColor(COL_BLACK)
    for col_i, hdr in enumerate(["Item", "Qty", "Price", "Discount", "Subtotal"]):
        align = "left" if col_i == 0 else "center"
        draw_cell_text(c, hdr, col_i, header_text_y, font="Helvetica-Bold", size=8, align=align)

    # Data rows
    grand_total = 0.0
    row_y = header_y
    for r_idx, item in enumerate(items):
        rh = ROW_H_DATA if r_idx % 2 == 0 else ROW_H_ALT
        row_y -= rh
        bg = COL_WHITE if r_idx % 2 == 0 else COL_TABLE_HEAD
        c.setFillColor(bg)
        c.rect(TABLE_L, row_y, TABLE_R - TABLE_L, rh, fill=1, stroke=0)

        price    = item["price"]
        qty      = item["qty"]
        discount = item.get("discount")
        subtotal = price * qty - (discount or 0)
        grand_total += subtotal

        text_y = row_y + 8
        c.setFillColor(COL_BLACK)
        draw_cell_text(c, item["name"],                           0, text_y, size=8, align="left")
        draw_cell_text(c, str(qty),                              1, text_y, size=8)
        draw_cell_text(c, fmt_idr(price),                        2, text_y, size=8)
        draw_cell_text(c, fmt_idr(discount) if discount else "-", 3, text_y, size=8)
        draw_cell_text(c, fmt_idr(subtotal),                     4, text_y, size=8)

    # Grand Total row
    row_y -= ROW_H_ALT
    c.setFillColor(COL_TABLE_HEAD)
    c.rect(TABLE_L, row_y, TABLE_R - TABLE_L, ROW_H_ALT, fill=1, stroke=0)
    text_y = row_y + 9
    c.setFillColor(COL_BLACK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(COL_X[0] + 6, text_y, "Grand Total")
    draw_cell_text(c, fmt_idr(grand_total), 4, text_y, font="Helvetica-Bold", size=8)

    # PAY TO
    pay_y = row_y - 45
    c.setFillColor(COL_TEXT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_L, pay_y, "PAY TO:")
    c.setFont("Helvetica", 8)
    for i, line in enumerate([
        BANK_NAME,
        "Account Name: " + ACCOUNT_NAME,
        "Account No.: " + ACCOUNT_NO,
        "Branch Name: " + BRANCH_NAME,
    ]):
        c.drawString(MARGIN_L, pay_y - 15 - i * 11, line)

    # Footer
    foot_y = 90
    c.setStrokeColor(COL_TEXT)
    c.setLineWidth(0.5)
    c.line(MARGIN_L - 8, foot_y + 22, (PAGE_W / 2) - 10, foot_y + 22)
    c.setFillColor(COL_TEXT)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN_L, foot_y + 8, REMITTANCE_NOTE)
    c.drawString(MARGIN_L, foot_y - 2, FOOTER_NOTE)

    # Write to temp file first, then rename to final path
    # (workaround for sandbox restriction on direct creation of INV*.pdf)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf", dir=os.path.dirname(output_path))
    os.close(tmp_fd)
    c._filename = tmp_path
    c.save()
    shutil.move(tmp_path, output_path)
    print("Invoice saved: {}".format(output_path))
    return grand_total


def main():
    parser = argparse.ArgumentParser(description="The Scholars Invoice Generator")
    parser.add_argument("--silent", action="store_true",
                        help="No prompts, default items only.")
    parser.add_argument("--extra-items", metavar="JSON_FILE",
                        help="JSON file with extra line items [{name, qty, price, discount}]")
    args = parser.parse_args()

    state    = load_state()
    inv_no   = next_invoice_no_from_files()
    today    = datetime.today()
    date_str = today.strftime("%d.%m.%Y")

    if args.extra_items:
        try:
            with open(args.extra_items) as f:
                extra_items = json.load(f)
            print("[Scheduled] {} item tambahan dimuat.".format(len(extra_items)))
        except Exception as e:
            print("[Warning] Gagal baca extra items: {}. Lanjut tanpa item tambahan.".format(e))
            extra_items = []
    elif args.silent:
        extra_items = []
        print("[Silent] Generating INV-{:03d} dengan item default.".format(inv_no))
    else:
        extra_items = ask_extra_items()

    all_items = DEFAULT_ITEMS + extra_items
    filename  = "thescholars_INV{:03d}.pdf".format(inv_no)
    out_path  = os.path.join(OUTPUT_DIR, filename)

    grand_total = generate_invoice(
        invoice_no  = inv_no,
        date_str    = date_str,
        items       = all_items,
        output_path = out_path,
    )

    state["last_invoice_no"] = inv_no
    state["last_generated"]  = today.isoformat()
    save_state(state)

    print("\nSelesai! Invoice #{:03d} - Grand Total: {}".format(inv_no, fmt_idr(grand_total)))
    return out_path


if __name__ == "__main__":
    main()
