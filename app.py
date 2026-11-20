import streamlit as st
import fitz
import re
import pandas as pd
import base64
import json
from PIL import Image
import pytesseract


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def extract_text_from_pdf(file_data):

    extracted_text = ""

    document = fitz.open(
        stream=file_data,
        filetype="pdf"
    )

    for page in document:

        page_text = page.get_text()

        extracted_text += page_text + "\n"

    return extracted_text


def extract_text_from_image(file_data):

    image = Image.open(file_data)

    text = pytesseract.image_to_string(image)

    return text


def detect_document_type(text):

    text_lower = text.lower()

    if "invoice" in text_lower:

        return "Invoice"

    elif "receipt" in text_lower:

        return "Receipt"

    elif "bill" in text_lower:

        return "Bill"

    elif "contract" in text_lower:

        return "Contract"

    elif "agreement" in text_lower:

        return "Agreement"

    else:

        return "General Document"


def extract_date(text):

    patterns = [

        r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",

        r"\b\d{4}[-/]\d{2}[-/]\d{2}\b"

    ]

    for pattern in patterns:

        result = re.findall(
            pattern,
            text
        )

        if result:

            return result[0]

    return "Not Found"


def extract_invoice_number(text):

    pattern = (
        r"(?i)"
        r"(?:invoice\s*(?:no|number|#)?"
        r"|bill\s*(?:no|number|#)?"
        r"|invoice\s*id)"
        r"\s*[:#-]?\s*"
        r"([A-Z0-9][A-Z0-9/-]{2,30})"
    )

    result = re.findall(
        pattern,
        text
    )

    if result:

        return result[0]

    return "Not Found"


def extract_amount(text):

    patterns = [

        r"(?:₹|Rs\.?|INR)\s?\d+(?:,\d{3})*(?:\.\d{2})?",

        r"(?:Total|Grand Total|Amount Due|Net Amount)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s?"
        r"\d+(?:,\d{3})*(?:\.\d{2})?"

    ]

    for pattern in patterns:

        result = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        if result:

            return result[0]

    return "Not Found"


def extract_vendor(text):

    lines = text.split("\n")

    company_keywords = [

        "Pvt. Ltd",
        "Private Limited",
        "Ltd.",
        "Limited",
        "LLP",
        "Inc.",
        "Corporation",
        "Company"

    ]

    for line in lines:

        clean_line = line.strip()

        for keyword in company_keywords:

            if keyword.lower() in clean_line.lower():

                return clean_line

    return "Not Found"


def calculate_status(data):

    found = 0

    total = 4

    for value in data.values():

        if value != "Not Found":

            found += 1

    percentage = int(
        (found / total) * 100
    )

    return percentage


# ==========================================
# APPLICATION HEADER
# ==========================================

st.title(
    "🤖 AI Document Intelligence & Workflow Automation"
)

st.caption(
    "Upload documents, extract information, classify documents, and download structured data."
)


# ==========================================
# FILE UPLOADER
# ==========================================

uploaded_file = st.file_uploader(
    "📤 Upload PDF or Image Document",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ]
)


# ==========================================
# PROCESS DOCUMENT
# ==========================================

if uploaded_file is not None:

    file_data = uploaded_file.getvalue()

    st.success(
        "Document uploaded successfully!"
    )


    # ======================================
    # FILE INFORMATION
    # ======================================

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "File Name",
            uploaded_file.name
        )

    with col2:

        st.metric(
            "File Type",
            uploaded_file.type
        )


    # ======================================
    # DOCUMENT PREVIEW
    # ======================================

    st.divider()

    st.subheader(
        "📄 Document Preview"
    )


    if uploaded_file.type == "application/pdf":

        base64_pdf = base64.b64encode(
            file_data
        ).decode(
            "utf-8"
        )

        pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="650px"
            style="
                border: 1px solid #cccccc;
                border-radius: 10px;
            ">
        </iframe>
        """

        st.components.v1.html(
            pdf_display,
            height=670
        )


    else:

        st.image(
            file_data,
            caption=uploaded_file.name,
            use_container_width=True
        )


    # ======================================
    # TEXT EXTRACTION
    # ======================================

    with st.spinner(
        "Processing document..."
    ):

        if uploaded_file.type == "application/pdf":

            extracted_text = extract_text_from_pdf(
                file_data
            )

        else:

            extracted_text = extract_text_from_image(
                file_data
            )


    # ======================================
    # DOCUMENT TYPE
    # ======================================

    document_type = detect_document_type(
        extracted_text
    )


    # ======================================
    # EXTRACT INFORMATION
    # ======================================

    date = extract_date(
        extracted_text
    )

    invoice_number = extract_invoice_number(
        extracted_text
    )

    amount = extract_amount(
        extracted_text
    )

    vendor = extract_vendor(
        extracted_text
    )


    extracted_data = {

        "Vendor / Company": vendor,

        "Date": date,

        "Invoice Number": invoice_number,

        "Amount": amount

    }


    extraction_status = calculate_status(
        extracted_data
    )


    # ======================================
    # DASHBOARD
    # ======================================

    st.divider()

    st.subheader(
        "📊 Document Intelligence Dashboard"
    )


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Document Type",
            document_type
        )

    with col2:

        st.metric(
            "Information Extracted",
            f"{extraction_status}%"
        )

    with col3:

        st.metric(
            "Fields Found",
            f"{sum(value != 'Not Found' for value in extracted_data.values())}/4"
        )


    # ======================================
    # INFORMATION CARDS
    # ======================================

    st.divider()

    st.subheader(
        "🔍 Extracted Information"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.info(
            f"🏢 **Vendor / Company**\n\n{vendor}"
        )

        st.info(
            f"📅 **Date**\n\n{date}"
        )


    with col2:

        st.info(
            f"🔢 **Invoice Number**\n\n{invoice_number}"
        )

        st.info(
            f"💰 **Amount**\n\n{amount}"
        )


    # ======================================
    # EXTRACTED TEXT
    # ======================================

    st.divider()

    with st.expander(
        "📝 View Extracted Text"
    ):

        st.text_area(
            "Extracted Text",
            extracted_text,
            height=400
        )


    # ======================================
    # PROFESSIONAL SUMMARY TABLE
    # ======================================

    st.divider()

    st.subheader(
        "📋 Structured Document Summary"
    )


    document_data = {

        "Field": list(
            extracted_data.keys()
        ),

        "Extracted Value": list(
            extracted_data.values()
        )

    }


    df = pd.DataFrame(
        document_data
    )


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # ======================================
    # DOWNLOAD SECTION
    # ======================================

    st.divider()

    st.subheader(
        "⬇️ Export Extracted Data"
    )


    col1, col2 = st.columns(2)


    # CSV DOWNLOAD

    csv_data = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    with col1:

        st.download_button(

            label="⬇️ Download CSV",

            data=csv_data,

            file_name="document_extracted_data.csv",

            mime="text/csv",

            use_container_width=True

        )


    # JSON DOWNLOAD

    json_data = json.dumps(
        {
            "document_type": document_type,
            "extraction_status": extraction_status,
            "data": extracted_data
        },
        indent=4
    )


    with col2:

        st.download_button(

            label="⬇️ Download JSON",

            data=json_data,

            file_name="document_extracted_data.json",

            mime="application/json",

            use_container_width=True

        )


    # ======================================
    # FOOTER
    # ======================================

    st.divider()

    st.caption(
        "AI Document Intelligence & Workflow Automation | Built using Python, Streamlit, PyMuPDF, OCR and Regular Expressions"
    )


else:

    st.info(
        "👆 Upload a PDF, invoice, receipt, or image document to start processing."
    )