# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Customers(Document):
    def before_save(self):
        self.fullname = f"{self.first_name} {self.surname}"
     
