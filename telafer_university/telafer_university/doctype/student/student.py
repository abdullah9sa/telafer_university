
import frappe
from frappe.model.document import Document
from frappe import _

class Student(Document):
    pass
    # def before_save(self):
    #     if frappe.db.exists("Student", {"owner": self.owner}):
    #         frappe.throw(_("A Student record already exists for this user."))