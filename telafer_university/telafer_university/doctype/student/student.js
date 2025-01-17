frappe.ui.form.on('Student', {
    refresh: function (frm) {
        if (frm.doc.status == "Accepted") {
            frm.add_custom_button(__('طباعة الملف'), function () {
                // Construct the URL for the print view
                const url = `/printview?doctype=Student&name=${frm.doc.name}&trigger_print=1&format=Student%20Print%20Format&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=ar`;
                
                // Open the URL in a new tab
                window.open(url, '_blank');
            }).addClass('bg-info');
        }
        
        if (!frm.is_new()) {

        if (frm.doc.status == "Pending"&& frappe.user.has_role('Student')) {
            frm.add_custom_button(__('Apply'), function () {
                frappe.msgprint(__("Information Applied Successfully"));
                frm.set_value('status', 'Applied');
                frm.save();
            }).addClass('bg-warning');
        }
        if (frm.doc.status == "Applied"&& (frappe.user.has_role('Registration Employee') || frappe.user.has_role('Registration Manager'))) {
            frm.add_custom_button(__('Reject'), function () {
                frm.set_value('status', 'Pending');
                frm.save();
                frappe.msgprint(__("Information Rejected"));

            }).addClass('bg-error');
            frm.add_custom_button(__('Accept'), function () {
                frappe.msgprint(__("Information Accepted Successfully"));
                frm.set_value('status', 'Accepted');
                frm.save();
            }).addClass('bg-success');
        }


        // Disable all fields if status is "Accepted" and user is not a Registration Manager
        // if (frm.doc.status === 'Accepted') {//&& !frappe.user.has_role('Registration Manager')) {
        if (frm.doc.status === 'Accepted' && !frappe.user.has_role('Registration Manager')) {
                Object.keys(frm.fields_dict).forEach(field => {
                frm.set_df_property(field, 'read_only', 1);
            });
            // Disable save
            frm.disable_save();
        }

        if (frm.doc.status === 'Applied' && frappe.user.has_role('Student')) {
            Object.keys(frm.fields_dict).forEach(field => {
            frm.set_df_property(field, 'read_only', 1);
            });
            // Disable save
            frm.disable_save();
        }


            const currentUrl = `${window.location.origin}/app/student/${frm.doc.name}`;
            const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(currentUrl)}&size=150x150`;
            frm.set_value('qr_code', qrCodeUrl);
            frm.refresh_field("qr_image");
        }

                // set debit_to to : default_receivable_account from doc.company's field
		frm.set_query("disrict", function () {
			return {
				filters: {
					province : frm.doc.province,
				},
			};
		});

        // set debit_to to : default_receivable_account from doc.company's field
        frm.set_query("department", function () {
            return {
                filters: {
                    faculty : frm.doc.faculty,
                },
            };
        });
        
    }
});

