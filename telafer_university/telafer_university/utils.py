import frappe
import json


@frappe.whitelist()
def submit_passed_students(students,year,result):
    students=json.loads(students)
    for std in students:
        student = frappe.get_doc("Student", std)
        if student:
            student.append(
                "student_study_log",
                {"year": year, "stage": student.stage, "finish_status": result},
            )
            stage_mapping = {
                "First": "Second",
                "Second": "Third",
                "Third": "Fourth",
                "Fourth": "Fifth",
            }
            
            if(result == "Passed"):
                student.stage = stage_mapping.get(student.stage, student.stage)
                
            student.save()
