# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ConsignedItems(Document):

	def on_submit(self):
		self.status = "Pending Evaluation"
