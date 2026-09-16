# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Bidders(Document):

    def validate(self):
        self.set_full_name()
        self.update_kyc_information()

    def set_full_name(self):

        if not self.user:
            return

        self.full_name = (
            frappe.db.get_value(
                "User",
                self.user,
                "full_name"
            ) or ""
        )

    def update_kyc_information(self):

        latest_kyc = frappe.db.get_value(
            "KYC Verification",
            {"bidder": self.name},
            ["name", "status"],
            order_by="creation desc",
            as_dict=True
        )

        if not latest_kyc:
            self.kyc_status = "Not Started"
            return

        self.kyc_status = latest_kyc.status
        self.last_kyc_sync = frappe.utils.now()

        if self.kyc_status == "Verified":

            self.kyc_verified_on = frappe.db.get_value(
                "KYC Verification",
                latest_kyc.name,
                "verification_date"
            )

            self.kyc_rejection_reason = ""

        elif self.kyc_status == "Rejected":

            self.kyc_rejection_reason = frappe.db.get_value(
                "KYC Verification",
                latest_kyc.name,
                "rejection_reason"
            )