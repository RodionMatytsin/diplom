const key = "kAlu7NqZwoWx7MaRwoXv9Qc4woZnAp==";
const main = document.getElementById("main");
let name_class = document.getElementById('name_class');

main.addEventListener('click', () => {
    get_classes();
});

name_class.addEventListener('input', function() {
    if (!/^[a-zA-ZА-Яа-я0-9_+=\s]*$/.test(name_class.value)) {
        name_class.value = name_class.value.replace(/[^a-zA-ZА-Яа-я0-9_+=\s]/g, '');
    }
});

document.getElementById("close_positions_wrapper_teacher_class_with_schoolchildren_for_admin").addEventListener('click', () => {
    sessionStorage.removeItem("class_guid");
    document.getElementById('schoolchildren_add').selectedIndex = 0;
    document.getElementById('teacher_add').selectedIndex = 0;
    document.getElementById('teacher_del').selectedIndex = 0;
    document.getElementById("positions_popup_teacher_class_with_schoolchildren_for_admin").style.display = 'none';
});

function add_class() {
    sendRequest(
        'POST',
        `/api/admin/classes?key=${key}`,
        true,
        {
            "name_class": name_class.value.trim()
        },
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_classes();
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function add_user_to_class(is_teacher = false) {
    let class_guid = sessionStorage.getItem("class_guid");
    let schoolchildren_add = document.getElementById('schoolchildren_add');
    let teacher_add = document.getElementById('teacher_add');

    if (is_teacher === false) {
        if (!schoolchildren_add.value) {
            show_error('Пожалуйста, выберите из списка школьника!', 'Ошибка');
            return;
        }
    } else {
        if (!teacher_add.value) {
            show_error('Пожалуйста, выберите из списка преподавателя!', 'Ошибка');
            return;
        }
    }

    sendRequest(
        'POST',
        `/api/admin/classes/${class_guid}/users/${(is_teacher === false) ? schoolchildren_add.value : teacher_add.value}?is_teacher=${is_teacher}&key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                if (is_teacher === false) {
                    get_users_to_class_for_admin(class_guid);
                    get_teacher_class_with_schoolchildren_for_admin(class_guid);
                } else {
                    get_users_to_class_for_admin(class_guid);
                }
            }, 500);
            show_error(data.message, 'Оповещение');
            schoolchildren_add.selectedIndex = 0;
            teacher_add.selectedIndex = 0;
            document.getElementById('teacher_del').selectedIndex = 0;
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function del_user_to_class() {
    let class_guid = sessionStorage.getItem("class_guid");
    let teacher_del = document.getElementById('teacher_del');

    if (!teacher_del.value) {
        show_error('Пожалуйста, выберите из списка преподавателя!', 'Ошибка');
        return;
    }

    sendRequest(
        'DELETE',
        `/api/admin/classes/${class_guid}/users/${teacher_del.value}?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_users_to_class_for_admin(class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
            document.getElementById('schoolchildren_add').selectedIndex = 0;
            document.getElementById('teacher_add').selectedIndex = 0;
            teacher_del.selectedIndex = 0;
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function del_class(class_guid) {
    sendRequest(
        'DELETE',
        `/api/admin/classes/${class_guid}?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_classes();
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function get_users_to_class_for_admin(class_guid) {
    sessionStorage.setItem("class_guid", class_guid);

    let schoolchildren_add = document.getElementById('schoolchildren_add'),
        teacher_add = document.getElementById('teacher_add'),
        teacher_del = document.getElementById('teacher_del');

    let placeholderSchoolchildrenAddOption = schoolchildren_add.querySelector('option'),
        placeholderTeacherAddOption = teacher_add.querySelector('option'),
        placeholderTeacherDelOption = teacher_del.querySelector('option');

    schoolchildren_add.innerHTML = '';
    schoolchildren_add.appendChild(placeholderSchoolchildrenAddOption);
    teacher_add.innerHTML = '';
    teacher_add.appendChild(placeholderTeacherAddOption);
    teacher_del.innerHTML = '';
    teacher_del.appendChild(placeholderTeacherDelOption);

    sendRequest(
        'GET',
        `/api/admin/classes/${class_guid}/users?key=${key}`,
        true,
        null,
        function (data) {
            let available_schoolchildren_list = data.data.available_schoolchildren;
            let available_teachers_list = data.data.available_teachers;
            let assigned_teachers_list = data.data.assigned_teachers;

            for (let i = 0; i < available_schoolchildren_list.length; i++) {
                let new_option = document.createElement('option');
                new_option.value = available_schoolchildren_list[i].user_guid;
                new_option.innerHTML = available_schoolchildren_list[i].user_fio;
                schoolchildren_add.appendChild(new_option);
            }

            for (let i = 0; i < available_teachers_list.length; i++) {
                let new_option = document.createElement('option');
                new_option.value = available_teachers_list[i].user_guid;
                new_option.innerHTML = available_teachers_list[i].user_fio;
                teacher_add.appendChild(new_option);
            }

            for (let i = 0; i < assigned_teachers_list.length; i++) {
                let new_option = document.createElement('option');
                new_option.value = assigned_teachers_list[i].user_guid;
                new_option.innerHTML = assigned_teachers_list[i].user_fio;
                teacher_del.appendChild(new_option);
            }

        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function del_schoolchildren(
    class_guid,
    schoolchildren_class_guid
) {
    sendRequest(
        'DELETE',
        `/api/admin/classes/${class_guid}/schoolchildren/${schoolchildren_class_guid}?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_users_to_class_for_admin(class_guid);
                get_teacher_class_with_schoolchildren_for_admin(class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function get_teacher_class_with_schoolchildren_for_admin(class_guid) {
    let positions_popup_teacher_class_with_schoolchildren_for_admin = document.getElementById("positions_popup_teacher_class_with_schoolchildren_for_admin");
    let teacher_class_with_schoolchildren_for_admin_list = document.getElementById("teacher_class_with_schoolchildren_for_admin_list");
    teacher_class_with_schoolchildren_for_admin_list.innerHTML = "";
    sendRequest(
        'GET',
        `/api/admin/classes/${class_guid}/schoolchildren?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            let teacher_class_with_schoolchildren_for_admin = data.data;

            let div_teacher_class_with_schoolchildren_for_admin_about = document.createElement('div'),
                div_teacher_class_with_schoolchildren_for_admin_name_class = document.createElement('div');

            div_teacher_class_with_schoolchildren_for_admin_about.id = teacher_class_with_schoolchildren_for_admin.class_guid;
            div_teacher_class_with_schoolchildren_for_admin_about.className = 'teacher_class_with_schoolchildren_for_admin_about';

            div_teacher_class_with_schoolchildren_for_admin_about.appendChild(div_teacher_class_with_schoolchildren_for_admin_name_class);
            div_teacher_class_with_schoolchildren_for_admin_name_class.className = 'teacher_class_with_schoolchildren_for_admin_name_class';
            div_teacher_class_with_schoolchildren_for_admin_name_class.innerHTML = '<b>Класс: </b>' + teacher_class_with_schoolchildren_for_admin.name_class;

            let schoolchildren_for_admin = teacher_class_with_schoolchildren_for_admin.schoolchildren;
            if (schoolchildren_for_admin.length === 0) {
                const teacher_class_with_schoolchildren_for_adminItem = document.createElement('div');
                teacher_class_with_schoolchildren_for_adminItem.classList.add('none_data');
                teacher_class_with_schoolchildren_for_adminItem.style.margin = '1% 0 0 0';
                teacher_class_with_schoolchildren_for_adminItem.style.fontSize = '2vw';
                teacher_class_with_schoolchildren_for_adminItem.innerHTML = 'Пока что в этом классе нет школьников ! :(';
                div_teacher_class_with_schoolchildren_for_admin_about.appendChild(teacher_class_with_schoolchildren_for_adminItem);
            }else{
                for (let j = 0; j < schoolchildren_for_admin.length; j++) {
                    let div_schoolchildren_for_admin_about = document.createElement('div'),
                        div_for_admin_user_fio = document.createElement('div'),
                        div_for_admin_estimation = document.createElement('div'),
                        div_for_admin_datetime_estimation_update = document.createElement('div'),
                        btn_for_admin_detail_about_to_schoolchildren = document.createElement('button'),
                        btn_for_admin_del_schoolchildren = document.createElement('button');

                    div_schoolchildren_for_admin_about.id = schoolchildren_for_admin[j].schoolchildren_class_guid;
                    div_schoolchildren_for_admin_about.className = 'schoolchildren_for_admin_about';

                    div_schoolchildren_for_admin_about.appendChild(div_for_admin_user_fio);
                    div_for_admin_user_fio.className = 'schoolchildren_for_admin_user_fio';
                    div_for_admin_user_fio.innerHTML = schoolchildren_for_admin[j].user_fio;

                    div_schoolchildren_for_admin_about.appendChild(div_for_admin_estimation);
                    div_for_admin_estimation.className = 'schoolchildren_div_for_admin_estimation';
                    div_for_admin_estimation.innerHTML = '<b>Оценка: </b>' + ((schoolchildren_for_admin[j].estimation) ? schoolchildren_for_admin[j].estimation : "-");

                    div_schoolchildren_for_admin_about.appendChild(div_for_admin_datetime_estimation_update);
                    div_for_admin_datetime_estimation_update.className = 'schoolchildren_for_admin_datetime_estimation_update';
                    div_for_admin_datetime_estimation_update.innerHTML = '<b>Дата и время обновления оценки: </b>' + ((schoolchildren_for_admin[j].datetime_estimation_update) ? schoolchildren_for_admin[j].datetime_estimation_update : "-");

                    div_schoolchildren_for_admin_about.appendChild(btn_for_admin_detail_about_to_schoolchildren);
                    btn_for_admin_detail_about_to_schoolchildren.className = 'btn_for_admin_detail_about_to_schoolchildren';
                    btn_for_admin_detail_about_to_schoolchildren.textContent = 'Подробнее о школьнике';
                    btn_for_admin_detail_about_to_schoolchildren.onclick = function() {
                        show_error(schoolchildren_for_admin[j].schoolchildren_class_guid, "Оповещение");
                    };

                    div_schoolchildren_for_admin_about.appendChild(btn_for_admin_del_schoolchildren);
                    btn_for_admin_del_schoolchildren.className = 'btn_for_admin_del_schoolchildren';
                    btn_for_admin_del_schoolchildren.textContent = 'Удалить школьника';
                    btn_for_admin_del_schoolchildren.onclick = function() {
                        del_schoolchildren(
                            teacher_class_with_schoolchildren_for_admin.class_guid,
                            schoolchildren_for_admin[j].schoolchildren_class_guid
                        );
                    };

                    div_teacher_class_with_schoolchildren_for_admin_about.appendChild(div_schoolchildren_for_admin_about);
                }
            }
            teacher_class_with_schoolchildren_for_admin_list.appendChild(div_teacher_class_with_schoolchildren_for_admin_about);
            positions_popup_teacher_class_with_schoolchildren_for_admin.style.display = 'flex';
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_class_for_dom(
    class_guid,
    name_class
) {
   let div_class = document.createElement('div'),
       div_class_about = document.createElement('div'),
       div_name_class = document.createElement('div'),
       div_del_class = document.createElement('div');

   div_class.id = class_guid;
   div_class.className = 'class_';
   div_class.appendChild(div_class_about);

   div_class_about.className = 'class_about';

   div_class_about.appendChild(div_name_class);
   div_name_class.className = 'name_class';
   div_name_class.innerHTML = '<b>Класс: </b>' + name_class;
   div_name_class.onclick = function () {
       get_users_to_class_for_admin(class_guid);
       get_teacher_class_with_schoolchildren_for_admin(class_guid);
   };

   div_class_about.appendChild(div_del_class);
   div_del_class.className = 'del_class';
   div_del_class.innerHTML = '+';
   div_del_class.onclick = function () {
       del_class(class_guid);
   };

   return div_class
}

function get_classes() {
    let classes_list = document.getElementById('classes_list');
    classes_list.innerHTML = '';
    sendRequest(
        'GET',
        `/api/admin/classes?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            let classes = data.data;
            if (classes.length === 0) {
                const classItem = document.createElement('div');
                classItem.classList.add('none_data');
                classItem.style.margin = '1% 0 0 0';
                classItem.style.fontSize = '2vw';
                classItem.innerHTML = 'Пока еще нет существующих классов ! :(';
                classes_list.appendChild(classItem);
            }else{
                for (let i = 0; i < classes.length; i++) {
                    classes_list.appendChild(
                        create_class_for_dom(
                            classes[i].guid,
                            classes[i].name
                        )
                    );
                }
            }
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}