
import frappe
from frappe.model.document import Document
from frappe import _

class Student(Document):
    def before_insert(self):
        # Check if the user has the "Student" role
        print(frappe.get_roles(self.owner))
        if "Student" in frappe.get_roles(self.owner):
            # Check if a Student record already exists for this user
            if frappe.db.exists("Student", {"owner": self.owner}):
                frappe.throw(_("A Student record already exists for this user."))
