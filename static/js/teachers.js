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
            localStorage.removeItem("is_teacher");
            window.location.href = "/";
        },
        function (data) {
            console.log(data);
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
            let is_teacher = localStorage.getItem("is_teacher");
            if (is_teacher === "true") {
                document.getElementById('name_user').innerText = data.data.fio;
                document.getElementById('phoneNumber').value = data.data.phone_number;
                document.getElementById('fio').value = data.data.fio;
                document.getElementById('day').value = data.data.birthday.day;
                document.getElementById('month').value = data.data.birthday.month;
                document.getElementById('year').value = data.data.birthday.year;
                document.getElementById('gender').value = data.data.gender;
            } else {
                window.location.href = "/";
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

document.getElementById("close_positions_wrapper_schoolchildren_by_user_guid").addEventListener('click', () => {
    document.getElementById("positions_popup_schoolchildren_by_user_guid").style.display = 'none';
    document.getElementById("schoolchildren_by_user_guid_list").innerText = '';
});

document.getElementById("close_positions_wrapper_teacher_class_with_schoolchildren").addEventListener('click', () => {
    document.getElementById("positions_popup_teacher_class_with_schoolchildren").style.display = 'none';
    document.getElementById("teacher_class_with_schoolchildren_list").innerText = '';
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

function create_personal_achievement_for_teacher(
    achievement_guid,
    attachment_guid,
    description,
    datetime_create
) {
    let div_achievement_about = document.createElement('div'),
        div_description = document.createElement('div'),
        div_datetime_create = document.createElement('div'),
        img_attachment_guid = document.createElement('img'),
        div_content_achievement = document.createElement('div');

    div_achievement_about.id = achievement_guid;
    div_achievement_about.className = 'achievement_about';

    div_achievement_about.appendChild(div_datetime_create);
    div_datetime_create.className = 'achievement_datetime_create';
    div_datetime_create.innerHTML = '<b>Дата/Время создания: </b>' + datetime_create;

    div_achievement_about.appendChild(div_content_achievement);
    div_content_achievement.className = 'content_achievement';

    div_content_achievement.appendChild(div_description);
    div_description.className = 'achievement_description';
    div_description.style.marginRight = '1%';
    div_description.innerHTML = '<b>Описание достижения: </b>' + description;

    div_content_achievement.appendChild(img_attachment_guid);
    img_attachment_guid.className = 'wrappers__container__achievement__icon';
    img_attachment_guid.id = 'profiled_photo';
    img_attachment_guid.src = `/api/attachments/${attachment_guid}` || '../static/img/addMedia.svg';
    img_attachment_guid.setAttribute('data-full', `/api/attachments/${attachment_guid}` || '../static/img/addMedia.svg');

    img_attachment_guid.onclick = function() {
        openModal(this.src);
    };

    return div_achievement_about;
}

function create_generated_recommendation_for_teacher(
    recommendation_guid,
    description,
    datetime_create
) {
    let div_recommendation_about = document.createElement('div'),
       div_description = document.createElement('div'),
       div_datetime_create = document.createElement('div');

   div_recommendation_about.id = recommendation_guid;
   div_recommendation_about.className = 'recommendation_about';

   div_recommendation_about.appendChild(div_datetime_create);
   div_datetime_create.className = 'recommendation_datetime_create';
   div_datetime_create.innerHTML = '<b>Дата/Время создания: </b>' + datetime_create;

   div_recommendation_about.appendChild(div_description);
   div_description.className = 'recommendation_description';
   div_description.innerHTML = '<b>Описание рекомендации: </b>' + description;

   return div_recommendation_about;
}

function recommendation_accept(recommendation_guid, schoolchildren_class_guid, class_guid) {
    sendRequest(
        'POST',
        `/api/recommendations/${recommendation_guid}/accept`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_schoolchildren_by_user_guid_for_teacher(class_guid, schoolchildren_class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function recommendation_reject(recommendation_guid, schoolchildren_class_guid, class_guid) {
    sendRequest(
        'POST',
        `/api/recommendations/${recommendation_guid}/reject`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_schoolchildren_by_user_guid_for_teacher(class_guid, schoolchildren_class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_generated_recommendation_suggested_for_teacher(
    recommendation_guid,
    description,
    datetime_create,
    schoolchildren_class_guid,
    class_guid
) {
    let div_recommendation_suggested = document.createElement('div'),
        div_recommendation_suggested_about = document.createElement('div'),
        div_description_suggested = document.createElement('div'),
        div_datetime_create_suggested = document.createElement('div'),
        btn_recommendation_accept = document.createElement('button'),
        btn_recommendation_reject = document.createElement('button');

    div_recommendation_suggested.id = recommendation_guid;
    div_recommendation_suggested.className = 'recommendation_suggested';

    div_recommendation_suggested.appendChild(div_recommendation_suggested_about);
    div_recommendation_suggested_about.className = 'recommendation_suggested_about';
    div_recommendation_suggested_about.style.margin = '0';

    div_recommendation_suggested_about.appendChild(div_datetime_create_suggested);
    div_datetime_create_suggested.className = 'recommendation_datetime_create_suggested';
    div_datetime_create_suggested.innerHTML = '<b>Дата/Время создания: </b>' + datetime_create;

    div_recommendation_suggested_about.appendChild(div_description_suggested);
    div_description_suggested.className = 'recommendation_description_suggested';
    div_description_suggested.innerHTML = '<b>Описание рекомендации: </b>' + description;

    div_recommendation_suggested.appendChild(btn_recommendation_reject);
    btn_recommendation_reject.className = 'btn_recommendation_reject';
    btn_recommendation_reject.textContent = 'Отклонить рекомендацию';
    btn_recommendation_reject.onclick = function() {
        recommendation_reject(recommendation_guid, schoolchildren_class_guid, class_guid);
    };

    div_recommendation_suggested.appendChild(btn_recommendation_accept);
    btn_recommendation_accept.className = 'btn_recommendation_accept';
    btn_recommendation_accept.textContent = 'Принять рекомендацию';
    btn_recommendation_accept.onclick = function() {
        recommendation_accept(recommendation_guid, schoolchildren_class_guid, class_guid);
    };

    return div_recommendation_suggested;
}

function accept_changes_for_test(
    test_guid,
    user_guid,
    schoolchildren_class_guid,
    class_guid
) {
    sendRequest(
        'PATCH',
        `/api/tests/${test_guid}/users/${user_guid}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_schoolchildren_by_user_guid_for_teacher(class_guid, schoolchildren_class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function generated_recommendation_schoolchildren(
    test_guid,
    schoolchildren_class_guid,
    class_guid
) {
    sendRequest(
        'POST',
        `/api/tests/${test_guid}/schoolchildren_class_guid/${schoolchildren_class_guid}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_schoolchildren_by_user_guid_for_teacher(class_guid, schoolchildren_class_guid);
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_passed_test_for_teacher(
    test_guid,
    name_test,
    datetime_create,
    is_accepted,
    test_details = [],
    user_guid,
    schoolchildren_class_guid,
    class_guid
) {
    let div_test_about = document.createElement('div'),
        div_test_header = document.createElement('div'),
        div_test_content = document.createElement('div'),
        div_name_test = document.createElement('div'),
        div_datetime_create = document.createElement('div'),
        div_test_details = document.createElement('div'),
        btn_test = document.createElement('div'),
        btn_generated_recommendation = document.createElement('div'),
        btn_accept_changes = document.createElement('div');

    div_test_about.className = 'test_about';

    if (is_accepted === true) {
        div_test_about.style.background = 'linear-gradient(127deg, rgba(70, 199, 63, 0.55) 0%, #ffffff 5%)';
    }

    div_test_header.className = 'test_header';
    div_test_content.className = 'test_content';

    div_test_content.appendChild(div_name_test);
    div_name_test.className = 'test_name';
    div_name_test.innerHTML = `<b>${name_test}</b>`;

    div_test_content.appendChild(div_datetime_create);
    div_datetime_create.className = 'test_datetime_create';
    div_datetime_create.innerHTML = '<b>Дата и время прохождения теста: </b>' + datetime_create;

    btn_test.id = test_guid;
    btn_test.className = 'btn_test';
    btn_test.style.backgroundImage = 'url(../static/img/dropDownIcons.svg)';
    btn_test.style.backgroundSize = '50%';
    btn_test.style.backgroundRepeat = 'no-repeat';
    btn_test.style.backgroundPosition = 'center';
    btn_test.onclick = function() {
        if (div_test_details.style.display === 'none' || div_test_details.style.display === '') {
            div_test_details.style.display = 'flex';
        } else {
            div_test_details.style.display = 'none';
        }
        btn_test.classList.toggle('flipped');
    };

    div_test_header.appendChild(div_test_content);
    div_test_header.appendChild(btn_test);

    div_test_details.className = 'test_details';
    div_test_details.style.display = 'none';

    test_details.forEach((item, index) => {
        const test_detail_about = document.createElement('div');
        test_detail_about.classList.add('test_detail_about');

        const questionName = document.createElement('div');
        questionName.id = item.question.question_id;
        questionName.classList.add('question_name');
        questionName.textContent = `Вопрос ${index + 1}: ${item.question.name}`;

        const questionScores = document.createElement('div');
        questionScores.classList.add('question_scores');
        questionScores.textContent = `Выставленная оценка к вопросу: `;
        for (let i = 1; i <= item.question.amount_of_points; i++) {
            const questionScore = document.createElement('div');
            questionScore.classList.add('question_score');
            questionScore.textContent = i;
            if (i === item.score) {
                questionScore.classList.add('selected');
            }
            questionScores.appendChild(questionScore);
        }

        const questionComment = document.createElement('div');
        questionComment.classList.add('question_comment');
        questionComment.textContent = `Комментарий к вопросу: ${(item.comment) ? item.comment : 'Школьник не оставил комментарий к данному вопросу'}`;

        test_detail_about.appendChild(questionName);
        test_detail_about.appendChild(questionScores);
        test_detail_about.appendChild(questionComment);

        div_test_details.appendChild(test_detail_about);
    })

    if (is_accepted === true) {
        div_test_details.appendChild(btn_generated_recommendation);
        btn_generated_recommendation.className = 'btn_generated_recommendation';
        btn_generated_recommendation.textContent = 'Сформировать рекомендацию для школьника';
        btn_generated_recommendation.onclick = function() {
            generated_recommendation_schoolchildren(
                test_guid,
                schoolchildren_class_guid,
                class_guid
            );
        };
    } else {
        div_test_details.appendChild(btn_accept_changes);
        btn_accept_changes.className = 'btn_accept_changes';
        btn_accept_changes.textContent = 'Принять изменения для формирования рекомендации';
        btn_accept_changes.onclick = function() {
            accept_changes_for_test(
                test_guid,
                user_guid,
                schoolchildren_class_guid,
                class_guid
            );
        };
    }

    div_test_about.appendChild(div_test_header);
    div_test_about.appendChild(div_test_details);

    return div_test_about;
}

function get_schoolchildren_by_user_guid_for_teacher(
    class_guid,
    schoolchildren_class_guid
) {
    let positions_popup_schoolchildren_by_user_guid = document.getElementById("positions_popup_schoolchildren_by_user_guid");
    let schoolchildren_by_user_guid_list = document.getElementById("schoolchildren_by_user_guid_list");
    schoolchildren_by_user_guid_list.style.margin = '1.5% 0 2.5% 0';
    schoolchildren_by_user_guid_list.innerHTML = "";
    sendRequest(
        'GET',
        `/api/teacher_classes/${class_guid}/schoolchildren/${schoolchildren_class_guid}`,
        true,
        null,
        function (data) {
            console.log(data);
            let schoolchildren_by_user_guid = data.data;

            let div_schoolchildren_by_user_guid_about = document.createElement('div');
            div_schoolchildren_by_user_guid_about.className = 'schoolchildren_by_user_guid_about';

            let div_personal_data_schoolchildren = document.createElement('div'),
                div_user_about = document.createElement('div');
            div_personal_data_schoolchildren.innerHTML = 'Личные данные школьника';
            div_personal_data_schoolchildren.style.margin = '1.5% 0';
            div_personal_data_schoolchildren.className = 'personal_data_schoolchildren';
            div_user_about.id = schoolchildren_by_user_guid.user.guid;
            div_user_about.className = 'user_about';
            div_user_about.style.width = '98%';

            div_schoolchildren_by_user_guid_about.appendChild(div_personal_data_schoolchildren);
            div_schoolchildren_by_user_guid_about.appendChild(div_user_about);

            let columnsDiv = document.createElement('div');
            columnsDiv.className = 'user_columns';

            let column1 = document.createElement('div');
            column1.className = 'user_column';

            let div_login = document.createElement('div'),
                div_phone_number = document.createElement('div');

            div_login.className = 'user_login';
            div_login.innerHTML = '<b>Логин: </b>' + schoolchildren_by_user_guid.user.login;
            div_phone_number.innerHTML = '<b>Номер телефона: </b>' + schoolchildren_by_user_guid.user.phone_number;

            column1.appendChild(div_login);
            column1.appendChild(div_phone_number);

            let column2 = document.createElement('div');
            column2.className = 'user_column';

            let div_fio = document.createElement('div'),
                div_birthday = document.createElement('div');

            div_fio.className = 'user_fio';
            div_fio.innerHTML = '<b>ФИО: </b>' + schoolchildren_by_user_guid.user.fio;
            let birthday = schoolchildren_by_user_guid.user.birthday;
            div_birthday.innerHTML = '<b>День рождения: </b>' + birthday.day + '.' + birthday.month + '.' + birthday.year;

            column2.appendChild(div_fio);
            column2.appendChild(div_birthday);

            let column3 = document.createElement('div');
            column3.className = 'user_column';

            let div_datetime_create = document.createElement('div'),
                div_gender = document.createElement('div');

            div_datetime_create.className = 'user_datetime_create';
            div_datetime_create.innerHTML = '<b>Дата и время регистрации: </b>' + schoolchildren_by_user_guid.user.datetime_create;
            div_gender.innerHTML = '<b>Пол: </b>' + schoolchildren_by_user_guid.user.gender;

            column3.appendChild(div_datetime_create);
            column3.appendChild(div_gender);

            columnsDiv.appendChild(column1);
            columnsDiv.appendChild(column2);
            columnsDiv.appendChild(column3);

            div_user_about.appendChild(columnsDiv);

            let div_personal_achievements_schoolchildren = document.createElement('div'),
                div_personal_achievements_schoolchildren_list = document.createElement('div');
            div_personal_achievements_schoolchildren.innerHTML = 'Личные достижения школьника';
            div_personal_achievements_schoolchildren.style.margin = '3.5% 0 1.5% 0';
            div_personal_achievements_schoolchildren.className = 'personal_achievements_schoolchildren';
            div_personal_achievements_schoolchildren_list.className = 'personal_achievements_schoolchildren_list';

            if (schoolchildren_by_user_guid.achievements.length === 0) {
                const achievementItem = document.createElement('div');
                achievementItem.classList.add('none_data');
                achievementItem.style.margin = '2.5% 0';
                achievementItem.style.fontSize = '2vw';
                achievementItem.innerHTML = 'Пока что у данного школьника нет личных достижений ! :(';
                div_personal_achievements_schoolchildren_list.appendChild(achievementItem);
            }else{
                for (let i = 0; i < schoolchildren_by_user_guid.achievements.length; i++) {
                    div_personal_achievements_schoolchildren_list.appendChild(
                        create_personal_achievement_for_teacher(
                            schoolchildren_by_user_guid.achievements[i].achievement_guid,
                            schoolchildren_by_user_guid.achievements[i].attachment_guid,
                            schoolchildren_by_user_guid.achievements[i].description,
                            schoolchildren_by_user_guid.achievements[i].datetime_create
                        )
                    );
                }
            }

            div_schoolchildren_by_user_guid_about.appendChild(div_personal_achievements_schoolchildren);
            div_schoolchildren_by_user_guid_about.appendChild(div_personal_achievements_schoolchildren_list);

            let div_generated_recommendations_schoolchildren = document.createElement('div'),
                div_generated_recommendations_schoolchildren_list = document.createElement('div');
            div_generated_recommendations_schoolchildren.innerHTML = 'Сформированные рекомендации для школьника';
            div_generated_recommendations_schoolchildren.style.margin = '3.5% 0 1.5% 0';
            div_generated_recommendations_schoolchildren.className = 'generated_recommendations_schoolchildren';
            div_generated_recommendations_schoolchildren_list.className = 'generated_recommendations_schoolchildren_list';

            if (schoolchildren_by_user_guid.recommendations.length === 0) {
                const recommendationItem = document.createElement('div');
                recommendationItem.classList.add('none_data');
                recommendationItem.style.margin = '2.5% 0';
                recommendationItem.style.fontSize = '2vw';
                recommendationItem.innerHTML = 'Пока что у данного школьника нет сформированных рекомендаций ! :(';
                div_generated_recommendations_schoolchildren_list.appendChild(recommendationItem);
            }else{
                for (let i = 0; i < schoolchildren_by_user_guid.recommendations.length; i++) {
                    div_generated_recommendations_schoolchildren_list.appendChild(
                        create_generated_recommendation_for_teacher(
                            schoolchildren_by_user_guid.recommendations[i].recommendation_guid,
                            schoolchildren_by_user_guid.recommendations[i].description,
                            schoolchildren_by_user_guid.recommendations[i].datetime_create
                        )
                    );
                }
            }

            div_schoolchildren_by_user_guid_about.appendChild(div_generated_recommendations_schoolchildren);
            div_schoolchildren_by_user_guid_about.appendChild(div_generated_recommendations_schoolchildren_list);

            let div_generated_recommendations_schoolchildren_suggested = document.createElement('div'),
                div_generated_recommendations_schoolchildren_suggested_list = document.createElement('div');
            div_generated_recommendations_schoolchildren_suggested.innerHTML = 'Сформированные рекомендации для школьника (предлагаемые)';
            div_generated_recommendations_schoolchildren_suggested.style.margin = '3.5% 0 1.5% 0';
            div_generated_recommendations_schoolchildren_suggested.className = 'generated_recommendations_schoolchildren_suggested';
            div_generated_recommendations_schoolchildren_suggested_list.className = 'generated_recommendations_schoolchildren_suggested_list';

            if (schoolchildren_by_user_guid.pending_recommendations.length === 0) {
                const pendingRecommendationItem = document.createElement('div');
                pendingRecommendationItem.classList.add('none_data');
                pendingRecommendationItem.style.margin = '2.5% 0';
                pendingRecommendationItem.style.fontSize = '2vw';
                pendingRecommendationItem.innerHTML = 'Пока что у данного школьника нет сформированных предложенных рекомендаций ! :(';
                div_generated_recommendations_schoolchildren_suggested_list.appendChild(pendingRecommendationItem);
            }else{
                for (let i = 0; i < schoolchildren_by_user_guid.pending_recommendations.length; i++) {
                    div_generated_recommendations_schoolchildren_suggested_list.appendChild(
                        create_generated_recommendation_suggested_for_teacher(
                            schoolchildren_by_user_guid.pending_recommendations[i].recommendation_guid,
                            schoolchildren_by_user_guid.pending_recommendations[i].description,
                            schoolchildren_by_user_guid.pending_recommendations[i].datetime_create,
                            schoolchildren_by_user_guid.schoolchildren_class_guid,
                            class_guid
                        )
                    );
                }
            }

            div_schoolchildren_by_user_guid_about.appendChild(div_generated_recommendations_schoolchildren_suggested);
            div_schoolchildren_by_user_guid_about.appendChild(div_generated_recommendations_schoolchildren_suggested_list);

            let div_passed_tests_schoolchildren = document.createElement('div'),
                div_passed_tests_schoolchildren_list = document.createElement('div');
            div_passed_tests_schoolchildren.innerHTML = 'Все пройденные тесты школьника';
            div_passed_tests_schoolchildren.style.margin = '3.5% 0 1.5% 0';
            div_passed_tests_schoolchildren.className = 'passed_tests_schoolchildren';
            div_passed_tests_schoolchildren_list.className = 'passed_tests_schoolchildren_list';
            div_passed_tests_schoolchildren_list.style.padding = '0.5% 0';

            if (schoolchildren_by_user_guid.tests.length === 0) {
                const testItem = document.createElement('div');
                testItem.classList.add('none_data');
                testItem.style.margin = '2.5% 0';
                testItem.style.fontSize = '2vw';
                testItem.innerHTML = 'Пока что данный школьник еще не проходил ни одного тестирования ! :(';
                div_passed_tests_schoolchildren_list.appendChild(testItem);
            }else{
                div_passed_tests_schoolchildren_list.style.marginTop = '-1%';
                div_passed_tests_schoolchildren_list.style.borderRadius = '0rem';
                div_passed_tests_schoolchildren_list.style.background = 'white';
                div_passed_tests_schoolchildren_list.style.boxShadow = '0 0 0px rgba(0, 0, 0, 0)';
                for (let i = 0; i < schoolchildren_by_user_guid.tests.length; i++) {
                    div_passed_tests_schoolchildren_list.appendChild(
                        create_passed_test_for_teacher(
                            schoolchildren_by_user_guid.tests[i].test_guid,
                            schoolchildren_by_user_guid.tests[i].name_test,
                            schoolchildren_by_user_guid.tests[i].datetime_create,
                            schoolchildren_by_user_guid.tests[i].is_accepted,
                            schoolchildren_by_user_guid.tests[i].test_details,
                            schoolchildren_by_user_guid.user.guid,
                            schoolchildren_by_user_guid.schoolchildren_class_guid,
                            class_guid
                        )
                    );
                }
            }

            div_schoolchildren_by_user_guid_about.appendChild(div_passed_tests_schoolchildren);
            div_schoolchildren_by_user_guid_about.appendChild(div_passed_tests_schoolchildren_list);

            schoolchildren_by_user_guid_list.appendChild(div_schoolchildren_by_user_guid_about);
            positions_popup_schoolchildren_by_user_guid.style.display = 'flex';
        },
        function (data) {
            console.log(data);
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
            div_teacher_class_with_schoolchildren_name_class.innerHTML = '<b>Учебный класс: </b>' + teacher_class_with_schoolchildren.name_class;

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

                    input_estimation.setAttribute('maxlength', '1');
                    input_estimation.addEventListener('input', function() {
                        this.value = this.value.replace(/[^2345]/g, '');
                    });

                    div_schoolchildren_about.id = schoolchildren[j].schoolchildren_class_guid;
                    div_schoolchildren_about.className = 'schoolchildren_about';

                    div_schoolchildren_about.appendChild(div_user_fio);
                    div_user_fio.className = 'schoolchildren_user_fio';
                    div_user_fio.innerHTML = schoolchildren[j].user_fio;

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
                        get_schoolchildren_by_user_guid_for_teacher(
                            teacher_class_with_schoolchildren.class_guid,
                            schoolchildren[j].schoolchildren_class_guid
                        );
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

   return div_teacher_class;
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