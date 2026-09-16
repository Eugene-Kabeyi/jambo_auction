# Copyright (c) 2026, Eugene Kabeyi
# For license information, please see license.txt

import frappe
import json

@frappe.whitelist()
def process_kyc(*args, **kwargs):
    """
    Unified API route. Explicitly isolates document state transitions
    to guarantee fields commit to database storage linearly.
    """
    settings = frappe.get_single("KYC Settings")
    if not settings.enable_kyc:
        frappe.throw("KYC processing is currently disabled globally.")

    request_data = {}
    if kwargs:
        request_data.update(kwargs)
    if hasattr(frappe, "form_dict") and frappe.form_dict:
        request_data.update(frappe.form_dict)

    bidder = request_data.get("bidder")
    document_type = request_data.get("document_type", "National ID")
    front_image = request_data.get("front_image") or request_data.get("document_image") or request_data.get("image_url")
    back_image = request_data.get("back_image")

    if "doc" in request_data:
        try:
            doc_payload = request_data.get("doc")
            if isinstance(doc_payload, str):
                doc_payload = json.loads(doc_payload)
            if isinstance(doc_payload, dict):
                bidder = doc_payload.get("bidder") or bidder
                document_type = doc_payload.get("document_type") or document_type
                front_image = doc_payload.get("front_image") or doc_payload.get("document_image") or doc_payload.get("image_url") or front_image
                back_image = doc_payload.get("back_image") or back_image
        except Exception:
            pass

    if not bidder:
        frappe.throw("Missing validation parameter: 'bidder' reference is required.")

    existing_kyc_name = frappe.db.get_value("KYC Verification", {"bidder": bidder}, "name")

    if existing_kyc_name:
        doc = frappe.get_doc("KYC Verification", existing_kyc_name)
    else:
        doc = frappe.new_doc("KYC Verification")
        doc.bidder = bidder

    # 1. Force clear historical extraction text parameters to trigger fresh evaluation runs
    doc.extracted_text = None
    doc.extracted_name = None
    doc.id_number = None
    doc.processing_status = "Processing"
    doc.status = "Pending"

    # 2. Assign active data payloads
    doc.document_type = document_type
    doc.front_image = front_image
    doc.back_image = back_image

    # 3. Call execution pipeline directly onto the in-memory document instance
    doc.run_full_kyc()
    
    # 4. Save the finalized object properties cleanly in a single operation
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "kyc_id": doc.name,
        "status": doc.status,
        "confidence": doc.confidence_score,
        "name": doc.extracted_name,
        "id_number": doc.id_number,
        "processing_status": doc.processing_status
    }
