# Copyright (c) 2026, Eugene Kabeyi
# For license information, please see license.txt

import frappe
import re
import os
from frappe.model.document import Document

class KYCVerification(Document):

    # REMOVED: before_save hook deleted to prevent double execution loops.

    # =====================================================
    # MASTER KYC PIPELINE
    # =====================================================
    def run_full_kyc(self):
        self.set_submitted_date()
        self.process_ocr()
        self.extract_basic_details()
        self.calculate_confidence()
        self.set_verification_details()
        self.update_bidder()

    # =====================================================
    # SET SUBMISSION TIME
    # =====================================================
    def set_submitted_date(self):
        if not self.submitted_on:
            self.submitted_on = frappe.utils.now()

    # =====================================================
    # OCR PROCESSING (LOCAL HIGH PERFORMANCE TESSERACT)
    # =====================================================
    def process_ocr(self):
        if not self.front_image:
            return

        # Simple gate: if text exists and we didn't wipe it, skip.
        if self.extracted_text:
            return

        settings = frappe.get_single("KYC Settings")
        if not settings.enable_kyc:
            return

        self.processing_status = "Processing"
        combined_text = []
        audit_logs = {}

        try:
            # 1. Parse Front Side Image
            front_text = self.extract_text_from_file(self.front_image)
            if front_text:
                combined_text.append(f"--- FRONT SIDE ---\n{front_text}")
                audit_logs["front_status"] = "Success"
            
            # 2. Parse Back Side Image if Document Type requires it
            if self.document_type == "National ID" and self.back_image:
                back_text = self.extract_text_from_file(self.back_image)
                if back_text:
                    combined_text.append(f"--- BACK SIDE ---\n{back_text}")
                    audit_logs["back_status"] = "Success"

            # 3. Consolidate Payloads
            if combined_text:
                self.extracted_text = "\n\n".join(combined_text)
                self.processing_status = "Completed"
                audit_logs["engine"] = "Local Tesseract 5.3.4"
                self.ocr_raw_response = frappe.as_json(audit_logs)
            else:
                self.processing_status = "Failed"
                self.ocr_raw_response = frappe.as_json({"error": "No text extracted from target assets"})

        except Exception:
            self.processing_status = "Failed"
            frappe.log_error(frappe.get_traceback(), "KYC Local Multi-OCR Error")

    # =====================================================
    # IMAGE BUFFER READER
    # =====================================================
    def extract_text_from_file(self, file_url):
        from PIL import Image
        import pytesseract

        if not file_url:
            return ""

        clean_path = file_url.lstrip("/")
        full_local_path = frappe.get_site_path("public", clean_path)

        if not os.path.exists(full_local_path):
            full_local_path = frappe.get_site_path(clean_path)

        if not os.path.exists(full_local_path):
            frappe.log_error(f"KYC asset path missing on disk: {full_local_path}", "KYC File Error")
            return ""

        try:
            with Image.open(full_local_path) as img:
                custom_config = r'--oem 3 --psm 3'
                return pytesseract.image_to_string(img, config=custom_config) or ""
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Tesseract read crash for: {file_url}")
            return ""

    # =====================================================
    # EXTRACT IDENTITY INFO
    # =====================================================
    def extract_basic_details(self):
        text = (self.extracted_text or "").lower()
        if not text:
            return

        bidder_name = frappe.db.get_value("Bidders", self.bidder, "full_name") or ""
        bidder_name_lower = bidder_name.lower()

        # Name Matching Engine
        if bidder_name_lower and bidder_name_lower in text:
            self.extracted_name = bidder_name
        else:
            parts = bidder_name_lower.split()
            match = sum(1 for p in parts if p in text)
            if parts and match >= max(1, len(parts) // 2):
                self.extracted_name = bidder_name

        # ID Number Detection Expressions
        patterns = [
            r"\b\d{8,16}\b",
            r"\b[a-zA-Z]{1,3}\d{5,12}\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, self.extracted_text or "")
            if match:
                self.id_number = match.group()
                break

    # =====================================================
    # CONFIDENCE ENGINE
    # =====================================================
    def calculate_confidence(self):
        confidence = 0.0
        text = (self.extracted_text or "").lower()

        if self.extracted_name:
            confidence += 0.5
        if self.id_number:
            confidence += 0.3
        if len(text) > 20:
            confidence += 0.1

        gov_keywords = ["republic", "government", "national", "identity", "passport", "citizen"]
        if any(k in text for k in gov_keywords):
            confidence += 0.1

        self.confidence_score = round(confidence, 2)
        settings = frappe.get_single("KYC Settings")
        threshold = settings.confidence_threshold or 0.7

        if confidence >= threshold:
            self.status = "Verified"
        elif confidence >= 0.4:
            self.status = "Pending"
        else:
            self.status = "Rejected"

    # =====================================================
    # VERIFICATION METADATA
    # =====================================================
    def set_verification_details(self):
        if self.status == "Verified":
            if not self.verification_date:
                self.verification_date = frappe.utils.now()
            if not self.verified_by:
                self.verified_by = frappe.session.user

    # =====================================================
    # UPDATE BIDDER 
    # =====================================================
    def update_bidder(self):
        if not self.bidder:
            return

        update_values = {
            "kyc_status": self.status,
            "last_kyc_sync": frappe.utils.now(),
            "latest_kyc": self.name,
            "kyc_provider": "Local Tesseract 5.3.4"
        }

        if self.status == "Verified":
            update_values["kyc_verified_on"] = self.verification_date
            update_values["status"] = "Active" 
        elif self.status == "Rejected":
            update_values["kyc_rejection_reason"] = getattr(self, "rejection_reason", "") or "Low validation score"

        frappe.db.set_value(
            "Bidders", 
            self.bidder, 
            update_values,
            update_modified=True
        )
