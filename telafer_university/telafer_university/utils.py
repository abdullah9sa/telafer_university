import frappe
import json

@frappe.whitelist()
def submit_passed_students(students,year):
    students=json.loads(students)
    for std in students:
        student = frappe.get_doc("Student", std)
        if student:
            student.append(
                "student_study_log",
                {"year": year, "stage": student.stage, "finish_status": "Passed"},
            )
            stage_mapping = {
                "First": "Second",
                "Second": "Third",
                "Third": "Fourth",
                "Fourth": "Fifth",
            }
            student.stage = stage_mapping.get(student.stage, student.stage)
            student.save()

