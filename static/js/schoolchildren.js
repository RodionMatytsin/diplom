const main = document.getElementById("main");
const testing = document.getElementById("testing");
const profile_settings = document.getElementById("profile_settings");
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
    testing.classList.remove("btn_active");
    profile_settings.classList.remove("btn_active");
    profile__settings__wrapper.style.display = 'none';
});

testing.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.add("btn_active");
    profile_settings.classList.remove("btn_active");
    profile__settings__wrapper.style.display = 'none';
});

profile_settings.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.remove("btn_active");
    profile_settings.classList.add("btn_active");
    profile__settings__wrapper.style.display = 'flex';
    get_achievements();
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
            if (data.data.is_teacher) {
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

function create_achievement() {
    let achievement = document.getElementById('achievement');
    sendRequest(
        'POST',
        '/api/achievements',
        true,
        {
            "description": achievement.value.trim()
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Оповещение');
            achievement.value = '';
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_achievement_for_dom(
    achievement_guid,
    description,
    datetime_create
) {
   let div_achievement = document.createElement('div'),
       div_achievement_about = document.createElement('div'),
       div_description = document.createElement('div'),
       div_datetime_create = document.createElement('div');

   div_achievement.id = achievement_guid;
   div_achievement.className = 'achievement';
   div_achievement.appendChild(div_achievement_about);

   div_achievement_about.className = 'achievement_about';

   div_achievement_about.appendChild(div_datetime_create);
   div_datetime_create.className = 'achievement_datetime_create';
   div_datetime_create.innerHTML = '<b>Дата/Время создания: </b>' + datetime_create;

   div_achievement_about.appendChild(div_description);
   div_description.className = 'achievement_description';
   div_description.innerHTML = '<b>Описание достижения: </b>' + description;

   return div_achievement
}

function get_achievements() {
    let achievements_list = document.getElementById('achievements_list');
    achievements_list.innerHTML = '';
    sendRequest(
        'GET',
        '/api/achievements',
        true,
        null,
        function (data) {
            console.log(data);
            let achievements = data.data;
            if (achievements.length === 0) {
                const achievementItem = document.createElement('div');
                achievementItem.classList.add('none_data');
                achievementItem.innerHTML = 'У вас сейчас нет никаких достижений :('
                achievements_list.appendChild(achievementItem);
            }else{
                for (let i = 0; i < achievements.length; i++) {
                    achievements_list.appendChild(
                        create_achievement_for_dom(
                            achievements[i].achievement_guid,
                            achievements[i].description,
                            achievements[i].datetime_create,
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