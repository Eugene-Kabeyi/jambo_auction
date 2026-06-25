import frappe
import requests


def get_settings():
    """
    Get KYC Settings singleton
    """
    return frappe.get_single("KYC Settings")


def run_ocr_space(image_url):
    """
    Send image URL to OCR.Space
    """

    settings = get_settings()

    url = "https://api.ocr.space/parse/image"

    payload = {
        "apikey": settings.ocr_api_key,
        "url": image_url,
        "language": settings.ocr_language or "eng",
        "isOverlayRequired": False
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        frappe.throw("Unable to connect to OCR.Space")

    result = response.json()

    if result.get("IsErroredOnProcessing"):
        frappe.throw("OCR processing failed")

    parsed_results = result.get("ParsedResults")

    if not parsed_results:
        frappe.throw("No text found in image")

    return parsed_results[0].get("ParsedText", "")


def extract_identity(text):
    """
    Simple extraction logic
    """

    full_name = ""
    id_number = ""

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if not id_number and any(char.isdigit() for char in line):
            if len(line) >= 6:
                id_number = line

        if not full_name:
            words = line.split()

            if len(words) >= 2:
                if all(word.replace("-", "").isalpha() for word in words):
                    full_name = line

    return full_name, id_number


@frappe.whitelist()
def process_kyc(bidder, image_url):

    settings = get_settings()

    if not settings.enable_kyc:
        frappe.throw("KYC is disabled")

    extracted_text = run_ocr_space(image_url)

    full_name, id_number = extract_identity(extracted_text)

    confidence = 0

    if full_name:
        confidence += 0.4

    if id_number:
        confidence += 0.4

    if len(extracted_text) > 20:
        confidence += 0.2

    if confidence >= settings.confidence_threshold:
        status = "Verified"
    elif confidence >= 0.5:
        status = "Pending"
    else:
        status = "Rejected"

    verification = frappe.new_doc("KYC Verification")

    verification.bidder = bidder
    verification.document_image = image_url
    verification.extracted_text = extracted_text
    verification.extracted_name = full_name
    verification.id_number = id_number
    verification.confidence_score = confidence
    verification.status = status

    verification.insert(ignore_permissions=True)

    bidder_doc = frappe.get_doc("Bidders", bidder)

    bidder_doc.latest_kyc = verification.name
    bidder_doc.kyc_status = status
    bidder_doc.last_kyc_sync = frappe.utils.now()

    if status == "Verified":
        bidder_doc.kyc_verified_on = frappe.utils.now()

    bidder_doc.save(ignore_permissions=True)

    return {
        "verification": verification.name,
        "status": status,
        "confidence": confidence
    }