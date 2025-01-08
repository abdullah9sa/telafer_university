frappe.listview_settings['Student'] = {
    onload: function (listview) {
        console.log("asd");
        if (frappe.user_roles.includes('Student')) {
            console.log("bbb");

            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Student',
                    filters: {
                        owner: frappe.session.user
                    },
                    fields: ['name']
                },
                callback: function (response) {
                    console.log(response);
                    $(".btn-primary").hide()

                }
            });
        }
    }
};
