frappe.pages['students-passing'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Students Passing',
		single_column: true
	});

	// Add filters
	const filters = {
		faculty: page.add_field({
			fieldname: 'faculty',
			label: 'Faculty',
			fieldtype: 'Link',
			options: 'Faculty',
			reqd: 1,
			onchange: function () {
				const faculty = filters.faculty.get_value();
				frappe.call({
					method: 'frappe.client.get_list',
					args: {
						doctype: 'Department',
						filters: { faculty: faculty },
						fields: ['name']
					},
					callback: function (r) {
						const departments = r.message.map(d => d.name);
						filters.department.df.options = [''].concat(departments).join('\n');
						filters.department.refresh();
					}
				});
			}
		}),
		department: page.add_field({
			fieldname: 'department',
			label: 'Department',
			fieldtype: 'Select',
			options: '',
			reqd: 1
		}),
		stage: page.add_field({
			fieldname: 'stage',
			label: 'Stage',
			fieldtype: 'Select',
			options: 'First\nSecond\nThird\nFourth\nFifth',
			reqd: 1
		}),
		year: page.add_field({
			fieldname: 'year',
			label: 'Educational Year',
			fieldtype: 'Link',
			options: 'Educational Year',
			reqd: 1
		})
	};


	// Add a container for the student grid
	const $gridContainer = $('<div>').appendTo(page.body);

	// Add a Get Students button
	page.add_field({
		fieldname: 'get_students',
		label: 'Get Students',
		fieldtype: 'Button',
		click: function () {
			const faculty = filters.faculty.get_value();
			const department = filters.department.get_value();
			const stage = filters.stage.get_value();

			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Student',
					filters: {
						faculty: faculty,
						department: department,
						stage: stage
					},
					fields: ['name', 'first_name', 'second_name', 'third_name']
				},
				callback: function (r) {
					const students = r.message || [];

					$gridContainer.empty();
					const $table = $('<table class="table table-bordered">').appendTo($gridContainer);
					const $tbody = $('<tbody>').appendTo($table);

					let row = null;
					students.forEach((student, index) => {
						if (index % 4 === 0) {
							row = $('<tr>').appendTo($tbody);
						}

						const studentCell = $('<td>')
							.addClass('student-cell')
							.css({
								cursor: 'pointer',
								textAlign: 'center',
								backgroundColor: '#f9f9f9'
							})
							.appendTo(row);

						const checkbox = $('<input>')
							.attr('type', 'checkbox')
							.attr('checked', true)
							.attr('data-student-id', student.name)
							.appendTo(studentCell);

						studentCell.append(
							`<div>${student.first_name} ${student.second_name} ${student.third_name}</div>`
						);

						studentCell.on('click', function () {
							const isChecked = checkbox.prop('checked');
							checkbox.prop('checked', !isChecked);
							$(this).css('background-color', isChecked ? '#f9f9f9' : '#d1ecf1');
						});
					});
				}
			});
		}
	});


	// Add a Submit button
	page.add_field({
		fieldname: 'submit',
		label: 'Submit',
		fieldtype: 'Button',
		click: function () {
			const checkedStudents = [];
			$gridContainer.find('input[type="checkbox"]:checked').each(function () {
				checkedStudents.push($(this).data('student-id'));
			});

			frappe.call({
				method: 'telafer_university.telafer_university.utils.submit_passed_students',
				args: { students: checkedStudents, year: filters.year.get_value() },
				callback: function (response) {
					frappe.msgprint(__('Successfully submitted selected students.'));
				}
			});
		}
	});

};
