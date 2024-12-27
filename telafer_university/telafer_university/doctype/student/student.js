frappe.ui.form.on('Student', {
    refresh: function (frm) {
        if (frm.doc.status == "Pending") {
            frm.add_custom_button(__('Apply'), function () {
                frappe.msgprint(__("Information Applied Successfully"));
                frm.set_value('status', 'Applied');
                frm.save();
            }).addClass('bg-warning');
        }
        if (frm.doc.status == "Applied") {
            frm.add_custom_button(__('Reject'), function () {
                frappe.msgprint(__("Information Rejected"));
                frm.set_value('status', 'Pending');
                frm.save();
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

        if (!frm.is_new()) {
            const currentUrl = `${window.location.origin}/app/student/${frm.doc.name}`;
            const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(currentUrl)}&size=150x150`;
            frm.set_value('qr_code', qrCodeUrl);
            frm.refresh_field("qr_image");
        }
    }
});
