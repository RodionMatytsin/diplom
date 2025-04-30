let login = document.getElementById('login'),
    password = document.getElementById('password'),
    role = document.getElementById('role'),
    signupLogin = document.getElementById('signupLogin'),
    signupPassword = document.getElementById('signupPassword'),
    phoneNumber = document.getElementById('phoneNumber'),
    fio = document.getElementById('fio'),
    day = document.getElementById('day'),
    month = document.getElementById('month'),
    year = document.getElementById('year')
    gender = document.getElementById('gender');


function signup_user() {
    sendRequest(
        'POST',
        '/api/signup',
        true,
        {
            "phone_number": phoneNumber.value,
            "fio": fio.value,
            "birthday": (year.value+'-'+month.value+'-'+day.value),
            "gender": gender.value,
            "role": role.value,
            "login": signupLogin.value,
            "password": signupPassword.value
        },
        function (data) {
            console.log(data);
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function login_user() {
    sendRequest(
        'POST',
        '/api/login',
        true,
        {
            "login": login.value,
            "password": password.value
        },
        function (data) {
            console.log(data);
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}
