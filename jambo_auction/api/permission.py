import frappe

def has_app_permission(user=None):
    if not user:
        user = frappe.session.user
        
    # Your validation logic using 'user' variable
    return True