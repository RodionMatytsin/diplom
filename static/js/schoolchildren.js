const main = document.getElementById("main");
const testing = document.getElementById("testing");
const profile_settings = document.getElementById("profile_settings");
const main__wrapper__schoolchildren_classes_list = document.getElementById("main__wrapper__schoolchildren_classes_list");
const main__wrapper__recommendations_list = document.getElementById("main__wrapper__recommendations_list");
const testing__wrapper = document.getElementById("testing__wrapper");
const main__wrapper__testing__list = document.getElementById("main__wrapper__testing__list");
const profile__settings__wrapper = document.getElementById("profile__settings__wrapper");
const logoExit = document.getElementById('logoExit');
let phoneNumber = document.getElementById('phoneNumber'),
    fio = document.getElementById('fio'),
    day = document.getElementById('day'),
    month = document.getElementById('month'),
    year = document.getElementById('year'),
    gender = document.getElementById('gender');
let attachment_guid ;

fio.addEventListener('input', function() {
    if (!/^[А-Яа-яЁё\s]*$/.test(fio.value)) {
        fio.value = fio.value.replace(/[^А-Яа-яЁё\s]/g, '');
    }
})

main.addEventListener('click', () => {
    main.classList.add("btn_active");
    testing.classList.remove("btn_active");
    profile_settings.classList.remove("btn_active");
    main__wrapper__schoolchildren_classes_list.style.display = 'flex';
    main__wrapper__recommendations_list.style.display = 'flex';
    testing__wrapper.style.display = 'none';
    main__wrapper__testing__list.style.display = 'none';
    profile__settings__wrapper.style.display = 'none';
    get_schoolchildren_classes();
    get_recommendations();
});

testing.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.add("btn_active");
    profile_settings.classList.remove("btn_active");
    main__wrapper__schoolchildren_classes_list.style.display = 'none';
    main__wrapper__recommendations_list.style.display = 'none';
    testing__wrapper.style.display = 'flex';
    main__wrapper__testing__list.style.display = 'flex';
    profile__settings__wrapper.style.display = 'none';
    get_questions();
});

profile_settings.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.remove("btn_active");
    profile_settings.classList.add("btn_active");
    main__wrapper__schoolchildren_classes_list.style.display = 'none';
    main__wrapper__recommendations_list.style.display = 'none';
    testing__wrapper.style.display = 'none';
    main__wrapper__testing__list.style.display = 'none';
    profile__settings__wrapper.style.display = 'flex';
    get_achievements();
    attachment_guid = null;
    const preview = document.getElementById('preview');
    preview.src = "../static/img/addMedia.svg";
    preview.classList.add("img_addMedia", "upload_label_img_modifier");
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

function get_questions() {
    sendRequest(
        'GET',
        `/api/questions`,
        true,
        null,
        function (data) {
            console.log(data);
            create_questions_for_dom(data.data);
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    );
}

function create_questions_for_dom(data) {
    let testing__list = document.getElementById('testing__list');
    testing__list.innerHTML = '';

    data.forEach((item, index) => {
        const questionContainer = document.createElement('div');
        questionContainer.classList.add('question_item');

        const questionTitle = document.createElement('div');
        questionTitle.id = item.question_id;
        questionTitle.classList.add('name_question');
        questionTitle.textContent = `Вопрос ${index + 1}: ${item.name}`;

        const scores = document.createElement('div');
        scores.classList.add('scores');
        scores.textContent = `Выставите оценку этому вопросу: `;
        for (let i = 1; i <= item.amount_of_points; i++) {
            const score = document.createElement('div');
            score.classList.add('score');
            score.setAttribute('data-value', i);
            score.textContent = i;

            score.addEventListener('click', function() {
                const allScores = scores.querySelectorAll('.score');
                allScores.forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
                scores.setAttribute('data-selected-score', this.getAttribute('data-value'));
            });

            scores.appendChild(score);
        }

        const commentTextarea = document.createElement('textarea');
        commentTextarea.placeholder = 'При необходимости введите комментарий к этому вопросу';
        commentTextarea.classList.add('comment_textarea');

        questionContainer.appendChild(questionTitle);
        questionContainer.appendChild(scores);
        questionContainer.appendChild(commentTextarea);

        testing__list.appendChild(questionContainer);
    })
}

function add_test_to_schoolchildren() {

    const details = [];
    const question_items = document.querySelectorAll('.question_item');

    question_items.forEach(item => {
        const question_id = item.querySelector('.name_question').id;
        const scores = item.querySelector('.scores');
        const comment = item.querySelector('.comment_textarea').value.trim();
        const score = scores.getAttribute('data-selected-score') || 0;
        details.push({
            question_id: parseInt(question_id),
            score: parseInt(score),
            comment: comment
        });
    });

    sendRequest(
        'POST',
        '/api/tests',
        true,
        {
            "details": details,
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

function sendRequestProfiledPhoto(method, url, async, data, onSuccess, onError) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, async);

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            const responseData = JSON.parse(xhr.responseText);
            onSuccess(responseData);
        } else {
            const errorData = JSON.parse(xhr.responseText);
            onError(errorData);
        }
    };

    xhr.onerror = function() {
        console.error("Ошибка сети");
        onError({ message: "Ошибка сети" });
    };

    xhr.send(data); // Отправляем данные
}

function onloadProfiledPhoto() {
    const fileInput = document.getElementById('profiled_photo');
    const preview = document.getElementById('preview');

    const file = fileInput.files[0];
    if (!(file instanceof File)) {
        console.error("Выбранный элемент не является файлом:", file);
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Предварительный просмотр изображения (если это изображение)
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    sendRequestProfiledPhoto(
        'POST',
        `/api/attachments?compress=true`,
        true,
        formData,
        function(data) {
            attachment_guid = data.data.guid;
            console.log(attachment_guid);
            preview.classList.remove("img_addMedia", "upload_label_img_modifier");
        },
        function(data) {
            show_error(data.message, 'Ошибка');
        }
    );
}

function create_achievement() {
    if  (attachment_guid === null){
        show_error(`Загрузите фото своего достижения`,"Уведомление");
    } else {
        sendRequest(
            'POST',
            '/api/achievements',
            true,
            {
                "attachment_guid": attachment_guid,
                "description": document.getElementById('achievement').value.trim()
            },
            function (data) {
                console.log(data);
                show_error(data.message, 'Оповещение');
                document.getElementById('achievement').value = '';

                const fileInput = document.getElementById('profiled_photo');
                const preview = document.getElementById('preview');

                fileInput.value = '';
                attachment_guid = null;

                preview.src = "../static/img/addMedia.svg";
                preview.classList.add("img_addMedia", "upload_label_img_modifier");
                preview.style.padding = "10%";
            },
            function (data) {
                console.log(data);
                show_error(data.message, 'Ошибка');
            }
        )
    }
}

function create_achievement_for_dom(
    achievement_guid,
    attachment_guid,
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

   return div_achievement;
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
                achievementItem.style.margin = '4% 0 3% 0';
                achievementItem.innerHTML = 'У Тебя сейчас нет никаких достижений ! :(';
                achievements_list.appendChild(achievementItem);
            }else{
                for (let i = 0; i < achievements.length; i++) {
                    achievements_list.appendChild(
                        create_achievement_for_dom(
                            achievements[i].achievement_guid,
                            achievements[i].attachment_guid,
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

function create_schoolchildren_class_for_dom(
    class_guid,
    name_class,
    estimation
) {
   let div_schoolchildren_class = document.createElement('div'),
       div_schoolchildren_class_about = document.createElement('div'),
       div_name_class = document.createElement('div'),
       div_estimation = document.createElement('div');

   div_schoolchildren_class.id = class_guid;
   div_schoolchildren_class.className = 'schoolchildren_class';
   div_schoolchildren_class.appendChild(div_schoolchildren_class_about);

   div_schoolchildren_class_about.className = 'schoolchildren_class_about';

   div_schoolchildren_class_about.appendChild(div_name_class);
   div_name_class.className = 'schoolchildren_class_name_class';
   div_name_class.innerHTML = '<b>Класс: </b>' + name_class;

   div_schoolchildren_class_about.appendChild(div_estimation);
   div_estimation.className = 'schoolchildren_class_estimation';
   div_estimation.innerHTML = '<b>Успеваемость: </b>' + ((estimation) ? estimation : "-");

   return div_schoolchildren_class;
}

function get_schoolchildren_classes() {
    let schoolchildren_classes_list = document.getElementById('schoolchildren_classes_list');
    schoolchildren_classes_list.innerHTML = '';
    sendRequest(
        'GET',
        '/api/schoolchildren_classes',
        true,
        null,
        function (data) {
            console.log(data);
            let schoolchildren_classes = data.data;
            if (schoolchildren_classes.length === 0) {
                const schoolchildren_classItem = document.createElement('div');
                schoolchildren_classItem.classList.add('none_data');
                schoolchildren_classItem.style.margin = '1% 0 0 0';
                schoolchildren_classItem.style.fontSize = '2vw';
                schoolchildren_classItem.innerHTML = 'Пока что Ты не состоишь ни в каком классе ! :(';
                schoolchildren_classes_list.appendChild(schoolchildren_classItem);
            }else{
                for (let i = 0; i < schoolchildren_classes.length; i++) {
                    schoolchildren_classes_list.appendChild(
                        create_schoolchildren_class_for_dom(
                            schoolchildren_classes[i].class_guid,
                            schoolchildren_classes[i].name_class,
                            schoolchildren_classes[i].estimation,
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

function create_recommendation_class_for_dom(
    recommendation_guid,
    description,
    datetime_create
) {
    let div_recommendation = document.createElement('div'),
       div_recommendation_about = document.createElement('div'),
       div_description = document.createElement('div'),
       div_datetime_create = document.createElement('div');

   div_recommendation.id = recommendation_guid;
   div_recommendation.className = 'recommendation';
   div_recommendation.appendChild(div_recommendation_about);

   div_recommendation_about.className = 'recommendation_about';

   div_recommendation_about.appendChild(div_datetime_create);
   div_datetime_create.className = 'recommendation_datetime_create';
   div_datetime_create.innerHTML = '<b>Дата/Время создания: </b>' + datetime_create;

   div_recommendation_about.appendChild(div_description);
   div_description.className = 'recommendation_description';
   div_description.innerHTML = '<b>Описание рекомендации: </b>' + description;

   return div_recommendation;
}

function get_recommendations() {
    let recommendations_list = document.getElementById('recommendations_list');
    recommendations_list.innerHTML = '';
    sendRequest(
        'GET',
        '/api/recommendations',
        true,
        null,
        function (data) {
            console.log(data);
            let recommendations = data.data;
            if (recommendations.length === 0) {
                const recommendationItem = document.createElement('div');
                recommendationItem.classList.add('none_data');
                recommendationItem.style.margin = '1% 0 0 0';
                recommendationItem.style.fontSize = '2vw';
                recommendationItem.innerHTML = 'Для Тебя сейчас нет никаких рекомендаций ! :(';
                recommendations_list.appendChild(recommendationItem);
            }else{
                for (let i = 0; i < recommendations.length; i++) {
                    recommendations_list.appendChild(
                        create_recommendation_class_for_dom(
                            recommendations[i].recommendation_guid,
                            recommendations[i].description,
                            recommendations[i].datetime_create,
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