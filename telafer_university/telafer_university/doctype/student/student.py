
import frappe
from frappe.model.document import Document
from frappe import _


class Student(Document):
    def before_save(self):
        if frappe.db.exists("Student", {"owner": self.owner}):
            # frappe.throw(_("A Student record already exists for this user."))
            frappe.throw(_("لا يمكن تسجيل طالب جديد بنفس المستخدم"))
            
            
            
            
            