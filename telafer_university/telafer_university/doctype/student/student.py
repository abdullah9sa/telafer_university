
import frappe
from frappe.model.document import Document
from frappe import _
import requests
import os

class Student(Document):
    def before_insert(self):
        # Check if the user has the "Student" role
        print(frappe.get_roles(self.owner))
        if "Student" in frappe.get_roles(self.owner):
            # Check if a Student record already exists for this user
            if frappe.db.exists("Student", {"owner": self.owner}):
                frappe.throw(_("A Student record already exists for this user."))
    
    def before_save(self):

        print(f"Starting after_insert for Student: {self.name}")
        print(f"QR Code field value: {self.qr_code}")
        
        if not self.qr_code:
            # Generate QR code URL if field is empty
            try:
                site_url = frappe.utils.get_url()
                student_url = f"{site_url}/app/student/{self.name}"
                qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?data={requests.utils.quote(student_url)}&size=150x150"
                print(f"Generated QR code URL: {qr_code_url}")
                self.qr_code = qr_code_url
            except Exception as e:
                    print(f"Error generating QR code: {str(e)}")
                    frappe.log_error(f"Error generating QR code: {str(e)}")
            else:
                print("QR code field has value, proceeding with download")
                try:
                    # Get the full URL of the attached file
                    file_url = frappe.utils.get_url(self.qr_code)
                    print(f"File URL: {file_url}")
                    # Download the image
                    print("Downloading image...")
                    response = requests.get(file_url)
                    print(f"Response status code: {response.status_code}")
                    if response.status_code == 200:
                        print("Download successful")
                        filename = os.path.basename(self.qr_code)
                        print(f"Filename: {filename}")
                        print("Creating new file document...")
                        file_doc = frappe.get_doc({
                            "doctype": "File",
                            "file_name": filename,
                            "content": response.content,
                            "attached_to_doctype": self.doctype,
                            "attached_to_name": self.name
                        })
                        file_doc.save()
                        print(f"New file saved with URL: {file_doc.file_url}")
                        print("Updating qr_code field...")
                        self.qr_code = file_doc.file_url
                        print("/n/n/n/n/n")
                        print(file_doc.file_url)
                        frappe.db.set_value("Student", self.name, "qr_code", file_doc.file_url)
                        frappe.db.commit()
                        print("QR code field updated successfully")
                    else:
                        print(f"Failed to download image, status code: {response.status_code}")
                except Exception as e:
                    print(f"Error in after_insert: {str(e)}")
                    frappe.log_error(f"Error downloading QR code: {str(e)}")
