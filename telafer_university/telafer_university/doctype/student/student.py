
import frappe
from frappe.model.document import Document
from frappe import _


class Student(Document):
    def before_insert(self):
        if frappe.get_all("Student", filters={"owner": self.owner}, limit_page_length=1):
            frappe.throw(_("لا يمكن تسجيل طالب جديد بنفس المستخدم"))

