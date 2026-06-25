# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Bidders(Document):

    def validate(self):
        self.set_full_name()
        self.update_kyc_information()

    def set_full_name(self):
        """
        Automatically populate full_name from User
        """

        if not self.user:
            return

        full_name = frappe.db.get_value(
            "User",
            self.user,
            "full_name"
        )

        if full_name:
            self.full_name = full_name

    def update_kyc_information(self):
        """
        Get the most recent KYC Verification record
        and update bidder KYC fields.
        """

        latest_kyc = frappe.get_all(
            "KYC Verification",
            filters={
                "bidder": self.name
            },
            fields=[
                "name",
                "status",
                "modified"
            ],
            order_by="creation desc",
            limit=1
        )

        if not latest_kyc:
            self.kyc_status = "Not Started"
            self.latest_kyc = None
            return

        kyc = latest_kyc[0]

        self.latest_kyc = kyc.name
        self.kyc_status = kyc.status
        self.last_kyc_sync = frappe.utils.now()

        if kyc.status == "Verified":

            verification_date = frappe.db.get_value(
                "KYC Verification",
                kyc.name,
                "modified"
            )

            self.kyc_verified_on = verification_date
            self.kyc_rejection_reason = None

        elif kyc.status == "Rejected":

            reason = frappe.db.get_value(
                "KYC Verification",
                kyc.name,
                "rejection_reason"
            )

            self.kyc_rejection_reason = reason