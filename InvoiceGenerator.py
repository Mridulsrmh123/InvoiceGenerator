import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont # For custom fonts

# --- Helper function for PDF Generation ---
def generate_invoice_pdf(data):
    """
    Generates an invoice PDF based on the provided data.

    Args:
        data (dict): A dictionary containing all invoice details:
            - 'invoice_title': Title of the invoice.
            - 'my_details': Multiline string of sender's details.
            - 'client_details': Multiline string of client's details.
            - 'deliverables': Multiline string of deliverables (one per line).
            - 'inference': Multiline string of inference/description (one per line).
            - 'total_amount': Total amount payable.
            - 'header_font': Font name for the invoice header.
            - 'body_font': Font name for the body text.
    """
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf")],
                                             title="Save Invoice PDF")
    if not file_path:
        return # User cancelled save dialog

    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # --- Custom Font Registration (Uncomment and modify if you have .ttf files) ---
        # To use a custom font like 'Baskerville Light', you need its .ttf file.
        # Place the .ttf file (e.g., 'Baskerville-Light.ttf') in the same directory
        # as this script. If the font file is not found, ReportLab will raise an error,
        # or the code will fall back to a standard font if implemented.
        #
        # Example for Baskerville Light:
        # try:
        #     pdfmetrics.registerFont(TTFont('Baskerville-Light', 'Baskerville-Light.ttf'))
        #     # It's good practice to register a font family if you have bold/italic variants
        #     # pdfmetrics.registerFontFamily('Baskerville-Light', normal='Baskerville-Light')
        # except Exception as e:
        #     print(f"Warning: Could not register Baskerville-Light font: {e}. "
        #           "Ensure 'Baskerville-Light.ttf' is in the script directory.")
        #     # You might want to force a fallback if the custom font is critical
        #     # data['body_font'] = 'Times-Roman' # Fallback for body text if custom fails

        # Define available standard ReportLab fonts for validation
        available_fonts = ["Helvetica", "Times-Roman", "Courier"]

        # Validate selected fonts or fall back to defaults if not standard or registered
        # If a custom font name (like 'Baskerville-Light') is selected, it's assumed
        # it has been registered above.
        header_font = data['header_font'] if data['header_font'] in available_fonts or pdfmetrics.hasFont(data['header_font']) else "Helvetica"
        body_font = data['body_font'] if data['body_font'] in available_fonts or pdfmetrics.hasFont(data['body_font']) else "Times-Roman"


        # --- Invoice Header ---
        # Set font for the header (e.g., Helvetica-Bold for a strong title)
        # Using a fixed larger size for the header
        c.setFont(header_font + "-Bold", 36) # Append "-Bold" for a bold version if available
        # Draw the header centered at the top
        c.drawCentredString(width / 2.0, height - 70, data['invoice_title'].upper())

        # --- My Details Paragraph (Left Aligned) ---
        c.setFont(body_font, 10) # Set font for body text
        textobject_my = c.beginText()
        textobject_my.setTextOrigin(inch, height - 150) # Position from left edge, down from top
        # Add each line of 'my_details' to the text object
        for line in data['my_details'].split('\n'):
            textobject_my.textLine(line)
        c.drawText(textobject_my) # Draw the text block on the canvas

        # --- Client Details Paragraph (Right Aligned) ---
        c.setFont(body_font, 10) # Ensure font is set for this block
        textobject_client = c.beginText()
        # Position from right edge (width - right_margin - some_offset)
        # 3 * inch roughly aligns it with the right side given standard margins
        textobject_client.setTextOrigin(width - (3.5 * inch), height - 150)
        # Add each line of 'client_details' to the text object
        for line in data['client_details'].split('\n'):
            textobject_client.textLine(line)
        c.drawText(textobject_client) # Draw the text block

        # --- Table for Deliverables and Inference ---
        styles = getSampleStyleSheet()
        p_style = styles['Normal']
        p_style.fontName = body_font # Apply the selected body font to table cell text
        p_style.fontSize = 10
        p_style.leading = 12 # Line spacing for paragraphs in table cells

        # Prepare table data, starting with headers
        table_data = [['Deliverables', 'Inference']]

        # Split multiline inputs into lists of items
        deliverables_list = data['deliverables'].split('\n')
        inference_list = data['inference'].split('\n')

        # Determine the maximum number of rows needed for the table
        max_len = max(len(deliverables_list), len(inference_list))

        # Populate table rows, ensuring consistency even if lists have different lengths
        for i in range(max_len):
            deliverable = deliverables_list[i] if i < len(deliverables_list) else ''
            inference = inference_list[i] if i < len(inference_list) else ''
            # Use Paragraph for text in cells to handle wrapping if content is long
            table_data.append([Paragraph(deliverable, p_style), Paragraph(inference, p_style)])

        # Add the total amount row at the bottom of the table
        table_data.append([
            Paragraph('<b>TOTAL PAYABLE:</b>', p_style), # Bold text for total label
            Paragraph(f'<b>{data["total_amount"]}</b>', p_style) # Bold text for total value
        ])

        # Calculate column widths. Each column takes roughly half the page width minus margins.
        # Adjusted for clarity and better layout.
        col_widths = [((width - 2 * inch) / 2.0), ((width - 2 * inch) / 2.0)]
        table = Table(table_data, colWidths=col_widths)

        # Define table styling
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#EEEEEE'), # Header background light grey
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'), # Header text color black
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),       # All text left aligned
            ('FONTNAME', (0, 0), (-1, 0), header_font + "-Bold"), # Header font bold
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),    # Padding below header
            ('BACKGROUND', (0, -1), (-1, -1), '#DDDDDD'), # Total row background slightly darker grey
            ('TEXTCOLOR', (0, -1), (-1, -1), '#000000'), # Total row text color black
            ('FONTNAME', (0, -1), (-1, -1), body_font + "-Bold"), # Total row font bold
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC'), # All borders light grey
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),       # Vertically align text to top of cells
            ('LEFTPADDING', (0, 0), (-1, -1), 5),      # Left padding for cells
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),     # Right padding for cells
            ('TOPPADDING', (0, 0), (-1, -1), 5),       # Top padding for cells
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),    # Bottom padding for cells
        ])

        table.setStyle(table_style)

        # Calculate table height to position it correctly on the page
        # wrapOn calculates the required width and height for the table given constraints
        table_width, table_height = table.wrapOn(c, width - 2 * inch, height) # Max width available, arbitrary height
        # Position the table below the details, with an inch left margin
        table.drawOn(c, inch, height - 300 - table_height) # Adjusted Y-position for better layout

        c.save() # Save the PDF file
        messagebox.showinfo("Success", "Invoice PDF generated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during PDF generation: {e}")

# --- GUI Setup ---
class InvoiceApp:
    """
    Tkinter application for generating invoices.
    Provides input fields for invoice details and a button to generate PDF.
    """
    def __init__(self, master):
        self.master = master
        master.title("Invoice Generator")
        master.geometry("700x750") # Set initial window size (width x height)
        master.resizable(True, True) # Allow window resizing

        # Configure column weights for resizing
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Create a main frame that can be scrolled if content exceeds window size
        self.canvas = tk.Canvas(master, borderwidth=0, highlightthickness=0)
        self.scrollable_frame = ttk.Frame(self.canvas) # Frame to hold all widgets
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y") # Pack scrollbar to the right
        self.canvas.pack(side="left", fill="both", expand=True) # Pack canvas to fill remaining space

        # Create a window in the canvas to place the scrollable_frame
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind events for dynamic resizing and scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")) # Update scroll region
        )
        self.canvas.bind('<Configure>', self._on_canvas_resize) # Adjust inner frame width on canvas resize

        # Configure scrollable_frame columns to expand
        self.scrollable_frame.grid_columnconfigure(0, weight=0) # Label column, fixed width
        self.scrollable_frame.grid_columnconfigure(1, weight=1) # Input field column, expands

        # --- Input Fields ---
        row_idx = 0 # Grid row counter

        # Invoice Title
        tk.Label(self.scrollable_frame, text="Invoice Title:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        self.invoice_title = tk.StringVar(value="SALES INVOICE") # Default value
        tk.Entry(self.scrollable_frame, textvariable=self.invoice_title, width=50, bd=2, relief="groove").grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        # My Details (Multiline Text)
        tk.Label(self.scrollable_frame, text="My Details (Name, Bank A/C, Branch etc.):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="nw", padx=10, pady=5) # sticky="nw" for top-left alignment
        self.my_details_text = tk.Text(self.scrollable_frame, height=5, width=60, bd=2, relief="groove")
        self.my_details_text.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        self.my_details_text.insert(tk.END, "Your Name\nYour Company Name\nYour Address, City, Pin Code\nGSTIN: ABCDEFGHIJKLMNO\nBank Name: XYZ Bank\nA/C No: 1234567890\nIFSC: XYZB0001234")
        row_idx += 1

        # Client Details (Multiline Text)
        tk.Label(self.scrollable_frame, text="Client Details (Name, GSTN, PAN, A/C No etc.):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="nw", padx=10, pady=5)
        self.client_details_text = tk.Text(self.scrollable_frame, height=5, width=60, bd=2, relief="groove")
        self.client_details_text.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        self.client_details_text.insert(tk.END, "Client Name\nClient Company\nClient Address, City, Pin Code\nGSTN: PQRSTUVWXY123Z\nPAN: ABCDE1234F\nClient A/C: 0987654321")
        row_idx += 1

        # Deliverables (Multiline Text, one per line for table rows)
        tk.Label(self.scrollable_frame, text="Deliverables (one per line):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="nw", padx=10, pady=5)
        self.deliverables_text = tk.Text(self.scrollable_frame, height=8, width=60, bd=2, relief="groove")
        self.deliverables_text.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        self.deliverables_text.insert(tk.END, "Consulting Services (Jan 2024)\nProject Management (Feb 2024)\nSoftware Development (Mar 2024)\nDocumentation & Training")
        row_idx += 1

        # Inference/Description (Multiline Text, one per line for table rows, matching deliverables)
        tk.Label(self.scrollable_frame, text="Inference/Description (one per line, matching deliverables):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="nw", padx=10, pady=5)
        self.inference_text = tk.Text(self.scrollable_frame, height=8, width=60, bd=2, relief="groove")
        self.inference_text.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        self.inference_text.insert(tk.END, "Detailed consultation on project strategy.\nOversight and coordination of project tasks.\nDevelopment of custom CRM module.\nUser manuals and hands-on training sessions.")
        row_idx += 1

        # Total Amount Payable
        tk.Label(self.scrollable_frame, text="Total Amount Payable:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        self.total_amount = tk.StringVar(value="INR 1,50,000.00")
        tk.Entry(self.scrollable_frame, textvariable=self.total_amount, width=50, bd=2, relief="groove").grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        # --- Font Selection ---
        # Available standard fonts in ReportLab.
        # If you register custom fonts (e.g., 'Baskerville-Light') in the PDF function,
        # you can add them to this list.
        available_fonts_reportlab = ["Helvetica", "Times-Roman", "Courier"]
        # If 'Baskerville-Light' is registered, add it here for selection:
        # available_fonts_reportlab.append("Baskerville-Light")

        tk.Label(self.scrollable_frame, text="Header Font:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        self.header_font_var = tk.StringVar(value="Helvetica") # Default header font
        self.header_font_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.header_font_var, values=available_fonts_reportlab, state="readonly", width=47)
        self.header_font_dropdown.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        tk.Label(self.scrollable_frame, text="Body Font:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        self.body_font_var = tk.StringVar(value="Times-Roman") # Default body font
        self.body_font_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.body_font_var, values=available_fonts_reportlab, state="readonly", width=47)
        self.body_font_dropdown.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        # --- Font Note for User ---
        tk.Label(self.scrollable_frame, text="Note on Custom Fonts:", font=("Arial", 9, "italic")).grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(self.scrollable_frame, text="For fonts like 'Baskerville Light', you need its .ttf file. Place it alongside this script and ensure it's registered in the PDF generation function.", wraplength=550, justify="left", font=("Arial", 9, "italic")).grid(row=row_idx+1, column=0, columnspan=2, sticky="w", padx=10, pady=0)
        row_idx += 2

        # --- Generate Button ---
        # Styled button for better appearance
        tk.Button(self.scrollable_frame, text="Generate Invoice PDF", command=self.on_generate_button_click,
                  bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), bd=3, relief="raised",
                  padx=20, pady=10).grid(row=row_idx, column=0, columnspan=2, pady=20)
        row_idx += 1

    def _on_canvas_resize(self, event):
        """
        Adjusts the width of the frame inside the canvas to match the canvas width.
        This ensures inner widgets expand correctly when the window is resized.
        """
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def on_generate_button_click(self):
        """
        Collects all data from the GUI fields and passes it to the PDF generation function.
        """
        data = {
            'invoice_title': self.invoice_title.get(),
            'my_details': self.my_details_text.get("1.0", tk.END).strip(), # Get all text from Text widget
            'client_details': self.client_details_text.get("1.0", tk.END).strip(),
            'deliverables': self.deliverables_text.get("1.0", tk.END).strip(),
            'inference': self.inference_text.get("1.0", tk.END).strip(),
            'total_amount': self.total_amount.get(),
            'header_font': self.header_font_var.get(),
            'body_font': self.body_font_var.get()
        }
        generate_invoice_pdf(data)

# --- Main Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk() # Create the main Tkinter window
    app = InvoiceApp(root) # Create an instance of the InvoiceApp
    root.mainloop() # Start the Tkinter event loop
