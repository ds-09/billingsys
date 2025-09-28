import streamlit as st 
import pandas as pd 
from fpdf import FPDF 
from datetime import datetime 
import math 

# --- PDF Generation Logic --- 
class PDF(FPDF): 
    def header(self): 
        self.set_y(10) 
        self.set_font('Helvetica', 'B', 18) 
        self.cell(0, 10, 'BACODA ENTERPRISES PVT LTD', 0, 1, 'C') 
        self.set_font('Helvetica', '', 10) 
        self.cell(0, 5, 'Plot no 33,34,35 Swagat Industrial Estate Masma Olpad Surat Gujarat - 394540', 0, 1, 'C') 
        self.cell(0, 5, 'GSTIN: 24AAJCB3255G1ZV | Phone: 9974040755', 0, 1, 'C') 
        self.line(10, self.get_y(), 200, self.get_y()) 
        self.ln(5) 

    def footer(self): 
        self.set_y(-15) 
        self.set_font('Helvetica', 'I', 8) 
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C') 

def create_invoice_pdf(invoice_data): 
    pdf = PDF('P', 'mm', 'A4') 
    pdf.add_page() 
    pdf.alias_nb_pages() 

    # --- Billing, Shipping & Invoice Info --- 
    box_start_y = pdf.get_y(); bill_to_width, ship_to_width, invoice_width, box_height = 80, 60, 50, 30 
    pdf.rect(10, box_start_y, bill_to_width, box_height); pdf.rect(10 + bill_to_width, box_start_y, ship_to_width, box_height); pdf.rect(10 + bill_to_width + ship_to_width, box_start_y, invoice_width, box_height) 
    pdf.set_xy(11, box_start_y + 1); pdf.set_font('Helvetica', 'B', 9); pdf.cell(0, 5, "BILL TO", 0, 1, 'L'); pdf.set_font('Helvetica', '', 9); pdf.set_x(11) 
    pdf.multi_cell(bill_to_width - 2, 4, f"NAME: {invoice_data['bill_to_name']}\nADDRESS: {invoice_data['bill_to_address']}\nSTATE: {invoice_data['bill_to_state']}\nGSTIN NO.: {invoice_data['bill_to_gstin']}", 0, 'L') 
    pdf.set_xy(11 + bill_to_width, box_start_y + 1); pdf.set_font('Helvetica', 'B', 9); pdf.cell(0, 5, "SHIP TO", 0, 1, 'L'); pdf.set_font('Helvetica', '', 9); pdf.set_x(11 + bill_to_width) 
    pdf.multi_cell(ship_to_width - 2, 4, f"NAME: {invoice_data['ship_to_name']}\nADDRESS: {invoice_data['ship_to_address']}\nSTATE: {invoice_data['ship_to_state']}\nGSTIN NO.: {invoice_data['ship_to_gstin']}", 0, 'L') 
    start_x = 12 + bill_to_width + ship_to_width; pdf.set_xy(start_x, box_start_y + 1) 
    pdf.set_font('Helvetica', 'B', 9); pdf.cell(0, 5, "INVOICE", 0, 1, 'L'); pdf.set_font('Helvetica', '', 9); label_width, colon_width = 22, 2 
    pdf.set_x(start_x); pdf.cell(label_width, 4, "INVOICE NO", 0, 0, 'L'); pdf.cell(colon_width, 4, ":", 0, 0, 'C'); pdf.cell(0, 4, f" {invoice_data['invoice_no']}", 0, 1, 'L') 
    pdf.set_x(start_x); pdf.cell(label_width, 4, "DATE", 0, 0, 'L'); pdf.cell(colon_width, 4, ":", 0, 0, 'C'); pdf.cell(0, 4, f" {invoice_data['date']}", 0, 1, 'L') 
    pdf.set_y(box_start_y + box_height) 
    pdf.set_font('Helvetica', 'B', 9); pdf.cell(30, 6, 'TRANSPORT:', 1, 0, 'L'); pdf.set_font('Helvetica', '', 9); pdf.cell(160, 6, f" {invoice_data['transport']}", 1, 1, 'L'); pdf.ln(5) 

    # --- Items Table --- 
    pdf.set_font('Helvetica', 'B', 8); col_widths = [10, 45, 45, 20, 20, 20, 30]; headers = ['SR NO', 'ITEM NAME', 'DESCRIPTION', 'HSN CODE', 'QTY', 'RATE', 'AMOUNT'] 
    for i, header in enumerate(headers): pdf.cell(col_widths[i], 7, header, 1, 0, 'C') 
    pdf.ln() 
    pdf.set_font('Helvetica', '', 8); items_df = invoice_data['items']; line_height = 6 
     
    for index, row in items_df.iterrows(): 
        x_start = pdf.get_x(); y_start = pdf.get_y() 
        # Create a list of lists, where each inner list is the text for a column, split into lines 
        wrapped_text = [ 
            [str(index + 1)], 
            pdf.multi_cell(col_widths[1], line_height, str(row['ITEM NAME']), split_only=True), 
            pdf.multi_cell(col_widths[2], line_height, str(row['DESCRIPTION']), split_only=True) 
        ] 
        # Find the max number of lines needed for this row 
        max_lines = max(len(col) for col in wrapped_text) 
        row_height = max_lines * line_height 

        # Draw the background and vertical lines for the entire row 
        pdf.rect(x_start, y_start, sum(col_widths), row_height) 
        for i in range(len(col_widths) - 1): 
             pdf.line(x_start + sum(col_widths[:i+1]), y_start, x_start + sum(col_widths[:i+1]), y_start + row_height) 

        # Print text line by line 
        for line_num in range(max_lines): 
            pdf.set_xy(x_start, y_start + (line_num * line_height)) 
            # Column 0: SR NO 
            sr_no_text = wrapped_text[0][line_num] if line_num < len(wrapped_text[0]) else '' 
            pdf.cell(col_widths[0], line_height, sr_no_text, 0, 0, 'C') 
            # Column 1: ITEM NAME 
            item_name_text = wrapped_text[1][line_num] if line_num < len(wrapped_text[1]) else '' 
            pdf.cell(col_widths[1], line_height, item_name_text, 0, 0, 'L') 
            # Column 2: DESCRIPTION 
            desc_text = wrapped_text[2][line_num] if line_num < len(wrapped_text[2]) else '' 
            pdf.cell(col_widths[2], line_height, desc_text, 0, 0, 'L') 

        # Print single-line content, vertically centered 
        y_centered = y_start + row_height / 2 - line_height / 4 
         
        try: hsn_code = str(int(row['HSN CODE'])) if pd.notna(row['HSN CODE']) else '' 
        except (ValueError, TypeError): hsn_code = str(row['HSN CODE']) 
        pdf.set_xy(x_start + sum(col_widths[:3]), y_centered); pdf.cell(col_widths[3], 0, hsn_code, 0, 0, 'C') 
        pdf.set_xy(x_start + sum(col_widths[:4]), y_centered); pdf.cell(col_widths[4], 0, str(row['QTY']), 0, 0, 'R') 
        pdf.set_xy(x_start + sum(col_widths[:5]), y_centered); pdf.cell(col_widths[5], 0, f"{row['RATE']:.2f}", 0, 0, 'R') 
        pdf.set_xy(x_start + sum(col_widths[:6]), y_centered); pdf.cell(col_widths[6], 0, f"{row['AMOUNT']:.2f}", 0, 0, 'R') 
         
        pdf.set_y(y_start + row_height) 
     
    y_after_items = pdf.get_y(); table_bottom_y = 190 
    if y_after_items < table_bottom_y: 
        pdf.rect(10, y_after_items, sum(col_widths), table_bottom_y - y_after_items) 
        for i in range(len(col_widths)-1): 
            x_pos = 10 + sum(col_widths[:i+1]) 
            pdf.line(x_pos, y_after_items, x_pos, table_bottom_y) 
    pdf.set_y(table_bottom_y) 
     
    # --- Footer Section --- 
    pdf.set_font('Helvetica', 'B', 8); pdf.cell(sum(col_widths[:4]), 6, 'TOTAL', 1, 0, 'L') 
    pdf.cell(col_widths[4], 6, str(invoice_data['total_qty']), 1, 0, 'R'); pdf.cell(col_widths[5], 6, '', 1, 0, 'C'); pdf.cell(col_widths[6], 6, f"{invoice_data['taxable_value']:.2f}", 1, 1, 'R') 
    y_after_total_line = pdf.get_y() 
     
    # --- Left Footer Column --- 
    remarks_label_width, remarks_text_width = 30, 70 
    pdf.set_x(10); pdf.set_font('Helvetica', 'B', 8); pdf.cell(remarks_label_width, 6, 'REMARKS', 'LRT', 0, 'L') 
    pdf.set_font('Helvetica', '', 8); pdf.multi_cell(remarks_text_width, 6, invoice_data['remarks'], 'LRT', 'L') 
    remarks_y_end = pdf.get_y(); pdf.line(10, remarks_y_end, 110, remarks_y_end) 
    pdf.set_x(10); pdf.set_font('Helvetica', 'B', 8); pdf.cell(100, 6, 'BANK DETAILS', 'LR', 1, 'L'); pdf.line(10, pdf.get_y(), 110, pdf.get_y()) 
    pdf.set_font('Helvetica', '', 8) 
    bank_details = {"BANK": invoice_data['bank_name'], "BRANCH": invoice_data['bank_branch'], "A/C NO": invoice_data['bank_ac_no'], "BANK IFSC": invoice_data['bank_ifsc']} 
    bank_y_content_start = pdf.get_y() 
    for label, value in bank_details.items(): 
        pdf.set_x(10); pdf.cell(25, 5, label, 'L', 0, 'L'); pdf.cell(75, 5, value, 'R', 1, 'L') 
    bank_y_end = pdf.get_y(); pdf.line(10, bank_y_end, 110, bank_y_end); pdf.line(35, bank_y_content_start, 35, bank_y_end) 

    # --- Right Footer Column --- 
    y_totals_start = y_after_total_line 
    pdf.set_y(y_totals_start); totals = [("TAXABLE VALUE", invoice_data['taxable_value']), (f"SGST @{invoice_data['sgst_percent']:.1f}%", invoice_data['sgst_amount']), (f"CGST @{invoice_data['cgst_percent']:.1f}%", invoice_data['cgst_amount']), (f"IGST @{invoice_data['igst_percent']:.1f}%", 0.00), ("BILL AMOUNT", invoice_data['bill_amount'])] 
    for i, (label, value) in enumerate(totals): 
        y = y_totals_start + (i * 6); pdf.set_xy(110, y); pdf.cell(45, 6, label, 1, 0, 'L'); pdf.cell(45, 6, f"{value:.2f}", 1, 1, 'R') 
         
    final_footer_y = max(bank_y_end, pdf.get_y()) 
    # --- Corrected Vertical Lines --- 
    pdf.line(10 + sum(col_widths[:4]), y_after_total_line, 10 + sum(col_widths[:4]), final_footer_y) # QTY Line 
    pdf.line(110, y_after_total_line, 110, final_footer_y) # Middle divider 
    pdf.line(10, y_after_total_line, 10, final_footer_y) # Left border 
    pdf.line(200, y_after_total_line, 200, final_footer_y) # Right border 

    return bytes(pdf.output()) 

# --- Streamlit App --- 
st.title("📄 Bacoda Enterprises Invoice Generator") 

if 'items_df' not in st.session_state: 
    st.session_state.items_df = pd.DataFrame([{"ITEM NAME": "Regular TShirt", "DESCRIPTION": "Round Neck (BLACK)", "HSN CODE": 6103, "QTY": 1, "RATE": 200.00}, {"ITEM NAME": "Short with a very long description to test text wrapping feature", "DESCRIPTION": "This is a Lycra NS Lycra short that is designed for maximum comfort and flexibility during workouts.", "HSN CODE": 6103, "QTY": 1, "RATE": 219.00}], columns=["ITEM NAME", "DESCRIPTION", "HSN CODE", "QTY", "RATE"]) 

with st.form("invoice_form"): 
    st.header("Invoice Details") 
    col1, col2 = st.columns(2); 
    with col1: 
        st.subheader("Bill To"); bill_to_name = st.text_input("Name", "Client Name"); bill_to_address = st.text_area("Address", "Client Address, 123 Street, City"); bill_to_state = st.text_input("State", "Gujarat"); bill_to_gstin = st.text_input("GSTIN", "24ABCDE1234F1Z5") 
    with col2: 
        st.subheader("Ship To"); ship_to_name = st.text_input("Name ", "Recipient Name"); ship_to_address = st.text_area("Address ", "Recipient Address, 456 Avenue, City"); ship_to_state = st.text_input("State ", "Gujarat"); ship_to_gstin = st.text_input("GSTIN ", "24ABCDE1234F1Z5") 
    st.divider() 
    col3, col4 = st.columns(2) 
    with col3: 
        invoice_no = st.text_input("Invoice Number", "11"); transport = st.text_input("Transport", "By Road") 
    with col4: 
        invoice_date = st.date_input("Date", datetime.now()); cgst_percent = st.number_input("CGST %", 0.0, value=2.5, step=0.1, format="%.2f"); sgst_percent = st.number_input("SGST %", 0.0, value=2.5, step=0.1, format="%.2f") 
    st.divider() 
    st.subheader("Items") 
    edited_df = st.data_editor(st.session_state.items_df, num_rows="dynamic", column_config={"HSN CODE": st.column_config.NumberColumn(format="%d", step=1), "RATE": st.column_config.NumberColumn(format="%.2f"), "QTY": st.column_config.NumberColumn(min_value=0)}, hide_index=True) 
    st.divider() 
    remarks = st.text_area("Remarks", "This is a long remark to test the text wrapping feature in the final PDF output. It should not overlap with the totals section.") 
    submitted = st.form_submit_button("Generate Invoice") 

if submitted: 
    # Filter out empty rows before processing 
    final_df = edited_df.dropna(subset=['ITEM NAME']).reset_index(drop=True) 
    final_df = final_df[final_df['ITEM NAME'].astype(str).str.strip() != ''] 

    if final_df.empty or final_df['QTY'].sum() == 0: 
        st.error("Please add at least one item with a name to the invoice.") 
    else: 
        final_df['QTY'] = pd.to_numeric(final_df['QTY'], errors='coerce').fillna(0); final_df['RATE'] = pd.to_numeric(final_df['RATE'], errors='coerce').fillna(0) 
        final_df["AMOUNT"] = (final_df["QTY"] * final_df["RATE"]).round(2) 
        taxable_value = final_df["AMOUNT"].sum(); total_qty = int(final_df["QTY"].sum()) 
        cgst_amount = (taxable_value * cgst_percent) / 100; sgst_amount = (taxable_value * sgst_percent) / 100 
        bill_amount = taxable_value + cgst_amount + sgst_amount 
        invoice_data = { 
            "bill_to_name": bill_to_name, "bill_to_address": bill_to_address, "bill_to_state": bill_to_state, "bill_to_gstin": bill_to_gstin, 
            "ship_to_name": ship_to_name, "ship_to_address": ship_to_address, "ship_to_state": ship_to_state, "ship_to_gstin": ship_to_gstin, 
            "invoice_no": invoice_no, "date": invoice_date.strftime("%d-%m-%Y"), "transport": transport, "items": final_df, 
            "total_qty": total_qty, "taxable_value": taxable_value, "cgst_percent": cgst_percent, "sgst_percent": sgst_percent, 
            "igst_percent": 5.0, "cgst_amount": cgst_amount, "sgst_amount": sgst_amount, "bill_amount": bill_amount, 
            "remarks": remarks, "bank_name": "HDFC BANK", "bank_branch": "Palanpur Canal Road", "bank_ac_no": "50200050866294", "bank_ifsc": "HDFC0006518" 
        } 
        pdf_bytes = create_invoice_pdf(invoice_data) 
        st.success("🎉 Invoice Generated Successfully!") 
        st.download_button(label="📥 Download Invoice PDF", data=pdf_bytes, file_name=f"Invoice_{invoice_no}_{bill_to_name.replace(' ', '_')}.pdf", mime="application/pdf")

