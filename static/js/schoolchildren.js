const main = document.getElementById("main");
const testing = document.getElementById("testing");
const profile_settings = document.getElementById("profile_settings");
const main__wrapper = document.getElementById("main__wrapper");
const main__wrapper__list = document.getElementById("main__wrapper__list");
const testing__wrapper = document.getElementById("testing__wrapper");
const testing__wrapper__list = document.getElementById("testing__wrapper__list");
const profile__settings__wrapper = document.getElementById("profile__settings__wrapper");
const profile__settings__wrapper__list = document.getElementById("profile__settings__wrapper__list");
const logoExit = document.getElementById('logoExit');


main.addEventListener('click', () => {
    main.classList.add("btn_active");
    testing.classList.remove("btn_active");
    profile_settings.classList.remove("btn_active"); // Исправлено
    main__wrapper.classList.add("hiden");
    main__wrapper__list.classList.add("hiden");
    testing__wrapper.classList.remove("hiden");
    testing__wrapper__list.classList.remove("hiden");
    profile__settings__wrapper.classList.remove("hiden");
    profile__settings__wrapper__list.classList.remove("hiden");
    main__wrapper__list.innerHTML='';
    testing__wrapper__list.innerHTML='';
    profile__settings__wrapper__list.innerHTML='';
})

testing.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.add("btn_active");
    profile_settings.classList.remove("btn_active"); // Исправлено
    main__wrapper.classList.remove("hiden");
    main__wrapper__list.classList.remove("hiden");
    testing__wrapper.classList.add("hiden");
    testing__wrapper__list.classList.add("hiden");
    profile__settings__wrapper.classList.remove("hiden");
    profile__settings__wrapper__list.classList.remove("hiden");
    main__wrapper__list.innerHTML='';
    testing__wrapper__list.innerHTML='';
    profile__settings__wrapper__list.innerHTML='';
})

profile_settings.addEventListener('click', () => {
    main.classList.remove("btn_active");
    testing.classList.remove("btn_active");
    profile_settings.classList.add("btn_active"); // Исправлено
    main__wrapper.classList.remove("hiden");
    main__wrapper__list.classList.remove("hiden");
    testing__wrapper.classList.remove("hiden");
    testing__wrapper__list.classList.remove("hiden");
    profile__settings__wrapper.classList.add("hiden");
    profile__settings__wrapper__list.classList.add("hiden");
    main__wrapper__list.innerHTML='';
    testing__wrapper__list.innerHTML='';
    profile__settings__wrapper__list.innerHTML='';
})

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
            if (data.data.is_teacher) {
                window.location.href = "/";
            } else {
                console.log(data);
                document.getElementById('name_user').innerText = data.data.fio;
            }
        },
        function (data) {
            console.log(data);
        }
    )
}

window.onload = get_user;