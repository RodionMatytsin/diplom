const main = document.getElementById("main");
const profile_settings = document.getElementById("profile_settings");
const main__wrapper = document.getElementById("main__wrapper");
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
            console.log(data)
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
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

window.onload = get_user;

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