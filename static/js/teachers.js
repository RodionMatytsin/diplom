const main = document.getElementById("main");
const profile_settings = document.getElementById("profile_settings");
const main__wrapper__teacher_classes_list = document.getElementById("main__wrapper__teacher_classes_list");
const profile__settings__wrapper = document.getElementById("profile__settings__wrapper");
const logoExit = document.getElementById('logoExit');
let phoneNumber = document.getElementById('phoneNumber'),
    fio = document.getElementById('fio'),
    day = document.getElementById('day'),
    month = document.getElementById('month'),
    year = document.getElementById('year'),
    gender = document.getElementById('gender');

fio.addEventListener('input', function() {
    if (!/^[А-Яа-яЁё\s]*$/.test(fio.value)) {
        fio.value = fio.value.replace(/[^А-Яа-яЁё\s]/g, '');
    }
})

main.addEventListener('click', () => {
    main.classList.add("btn_active");
    profile_settings.classList.remove("btn_active");
    main__wrapper__teacher_classes_list.style.display = 'flex';
    profile__settings__wrapper.style.display = 'none';
    get_teacher_classes();
});

profile_settings.addEventListener('click', () => {
    main.classList.remove("btn_active");
    profile_settings.classList.add("btn_active");
    main__wrapper__teacher_classes_list.style.display = 'none';
    profile__settings__wrapper.style.display = 'flex';
});

logoExit.addEventListener('mouseover', function() {
    logoExit.src = '../static/img/logo_exit_red.svg';
});

logoExit.addEventListener('mouseout', function() {
    logoExit.src = '../static/img/logo_exit_black.svg';
});

function logout() {
    sendRequest(
        'POST',
        '/api/logout',
        true,
        null,
        function (data) {
            console.log(data);
            window.location.href = "/";
        },
        function (data) {
            console.log(data);
            window.location.href = "/";
        }
    )
}

function get_user() {
    sendRequest(
        'GET',
        '/api/users/me',
        true,
        null,
        function (data) {
            console.log(data);
            if (!data.data.is_teacher) {
                window.location.href = "/";
            } else {
                document.getElementById('name_user').innerText = data.data.fio;
                document.getElementById('phoneNumber').value = data.data.phone_number;
                document.getElementById('fio').value = data.data.fio;
                document.getElementById('day').value = data.data.birthday.day;
                document.getElementById('month').value = data.data.birthday.month;
                document.getElementById('year').value = data.data.birthday.year;
                document.getElementById('gender').value = data.data.gender;
            }
        },
        function (data) {
            console.log(data);
        }
    )
}

function update_user() {
    sendRequest(
        'PATCH',
        '/api/users',
        true,
        {
            "phone_number": phoneNumber.value,
            "fio": fio.value.trim(),
            "birthday": (year.value+'-'+month.value+'-'+day.value),
            "gender": gender.value
        },
        function (data) {
            console.log(data);
            get_user();
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

window.onload = get_user;

document.getElementById("close_positions_wrapper_teacher_class_with_schoolchildren").addEventListener('click', () => {
    document.getElementById("positions_popup_teacher_class_with_schoolchildren").style.display = 'none';
});

function update_estimation_to_schoolchildren(schoolchildren_class_guid, estimation) {
    sendRequest(
        'PATCH',
        '/api/teacher_classes/estimation',
        true,
        {
            "schoolchildren_class_guid": schoolchildren_class_guid,
            "estimation": Number(estimation)
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function get_teacher_class_with_schoolchildren(class_guid) {
    let positions_popup_teacher_class_with_schoolchildren = document.getElementById("positions_popup_teacher_class_with_schoolchildren");
    let teacher_class_with_schoolchildren_list = document.getElementById("teacher_class_with_schoolchildren_list");
    teacher_class_with_schoolchildren_list.innerHTML = "";
    sendRequest(
        'GET',
        `/api/teacher_classes/${class_guid}/schoolchildren`,
        true,
        null,
        function (data) {
            console.log(data);
            let teacher_class_with_schoolchildren = data.data;

            let div_teacher_class_with_schoolchildren_about = document.createElement('div'),
                div_teacher_class_with_schoolchildren_name_class = document.createElement('div');

            div_teacher_class_with_schoolchildren_about.id = teacher_class_with_schoolchildren.class_guid;
            div_teacher_class_with_schoolchildren_about.className = 'teacher_class_with_schoolchildren_about';

            div_teacher_class_with_schoolchildren_about.appendChild(div_teacher_class_with_schoolchildren_name_class);
            div_teacher_class_with_schoolchildren_name_class.className = 'teacher_class_with_schoolchildren_name_class';
            div_teacher_class_with_schoolchildren_name_class.innerHTML = '<b>Класс: </b>' + teacher_class_with_schoolchildren.name_class;

            let schoolchildren = teacher_class_with_schoolchildren.schoolchildren;
            if (schoolchildren.length === 0) {
                const teacher_class_with_schoolchildrenItem = document.createElement('div');
                teacher_class_with_schoolchildrenItem.classList.add('none_data');
                teacher_class_with_schoolchildrenItem.style.margin = '1% 0 0 0';
                teacher_class_with_schoolchildrenItem.style.fontSize = '2vw';
                teacher_class_with_schoolchildrenItem.innerHTML = 'Пока что в этом классе нет школьников ! :(';
                div_teacher_class_with_schoolchildren_about.appendChild(teacher_class_with_schoolchildrenItem);
            }else{
                for (let j = 0; j < schoolchildren.length; j++) {
                    let div_schoolchildren_about = document.createElement('div'),
                        div_user_fio = document.createElement('div'),
                        label_estimation = document.createElement('div'),
                        input_estimation = document.createElement('input'),
                        div_datetime_estimation_update = document.createElement('div'),
                        btn_detail_about_to_schoolchildren = document.createElement('button'),
                        btn_update_estimation_to_schoolchildren = document.createElement('button');

                    div_schoolchildren_about.id = schoolchildren[j].schoolchildren_class_guid;
                    div_schoolchildren_about.className = 'schoolchildren_about';

                    div_schoolchildren_about.appendChild(div_user_fio);
                    div_user_fio.className = 'schoolchildren_user_fio';
                    div_user_fio.innerHTML = '<b>ФИО: </b>' + schoolchildren[j].user_fio;

                    div_schoolchildren_about.appendChild(label_estimation);
                    label_estimation.className = 'schoolchildren_label_estimation';
                    label_estimation.innerHTML = '<b>Оценка: </b>';
                    label_estimation.appendChild(input_estimation);
                    input_estimation.className = 'schoolchildren_input_estimation';
                    input_estimation.value = schoolchildren[j].estimation;

                    div_schoolchildren_about.appendChild(div_datetime_estimation_update);
                    div_datetime_estimation_update.className = 'schoolchildren_datetime_estimation_update';
                    div_datetime_estimation_update.innerHTML = '<b>Дата и время обновления оценки: </b>' + ((schoolchildren[j].datetime_estimation_update) ? schoolchildren[j].datetime_estimation_update : "-");

                    div_schoolchildren_about.appendChild(btn_detail_about_to_schoolchildren);
                    btn_detail_about_to_schoolchildren.className = 'btn_detail_about_to_schoolchildren';
                    btn_detail_about_to_schoolchildren.textContent = 'Подробнее о школьнике';
                    btn_detail_about_to_schoolchildren.onclick = function() {
                        show_error(schoolchildren[j].schoolchildren_class_guid, "Оповещение");
                    };

                    div_schoolchildren_about.appendChild(btn_update_estimation_to_schoolchildren);
                    btn_update_estimation_to_schoolchildren.className = 'btn_update_estimation_to_schoolchildren';
                    btn_update_estimation_to_schoolchildren.textContent = 'Сохранить изменения';
                    btn_update_estimation_to_schoolchildren.onclick = function() {
                        update_estimation_to_schoolchildren(
                            schoolchildren[j].schoolchildren_class_guid,
                            input_estimation.value
                        );
                    };

                    div_teacher_class_with_schoolchildren_about.appendChild(div_schoolchildren_about);
                }
            }
            teacher_class_with_schoolchildren_list.appendChild(div_teacher_class_with_schoolchildren_about);
            positions_popup_teacher_class_with_schoolchildren.style.display = 'flex';
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_teacher_class_for_dom(
    class_guid,
    name_class
) {
   let div_teacher_class = document.createElement('div'),
       div_teacher_class_about = document.createElement('div'),
       div_name_class = document.createElement('div');

   div_teacher_class.id = class_guid;
   div_teacher_class.className = 'teacher_class';
   div_teacher_class.appendChild(div_teacher_class_about);

   div_teacher_class_about.className = 'teacher_class_about';

   div_teacher_class_about.appendChild(div_name_class);
   div_name_class.className = 'teacher_class_name_class';
   div_name_class.innerHTML = '<b>Класс: </b>' + name_class;

   div_teacher_class.onclick = function () {
       get_teacher_class_with_schoolchildren(class_guid);
   };

   return div_teacher_class
}

function get_teacher_classes() {
    let teacher_classes_list = document.getElementById('teacher_classes_list');
    teacher_classes_list.innerHTML = '';
    sendRequest(
        'GET',
        '/api/teacher_classes',
        true,
        null,
        function (data) {
            console.log(data);
            let teacher_classes = data.data;
            if (teacher_classes.length === 0) {
                const teacher_classItem = document.createElement('div');
                teacher_classItem.classList.add('none_data');
                teacher_classItem.style.margin = '1% 0 0 0';
                teacher_classItem.style.fontSize = '2vw';
                teacher_classItem.innerHTML = 'Пока что Вы не видите ни одного своего учебного класса ! :(';
                teacher_classes_list.appendChild(teacher_classItem);
            }else{
                for (let i = 0; i < teacher_classes.length; i++) {
                    teacher_classes_list.appendChild(
                        create_teacher_class_for_dom(
                            teacher_classes[i].class_guid,
                            teacher_classes[i].name_class
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