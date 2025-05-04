let login = document.getElementById('login'),
    password = document.getElementById('password'),
    role = document.getElementById('role'),
    signupLogin = document.getElementById('signupLogin'),
    signupPassword = document.getElementById('signupPassword'),
    phoneNumber = document.getElementById('phoneNumber'),
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

login.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_\-]+$/.test(login.value)) {
        login.value = login.value.replace(/[^a-zA-Z0-9_\-]/g, '');
    }
});

password.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_.\-!]+$/.test(password.value)) {
        password.value = password.value.replace(/[^a-zA-Z0-9_.\-!]/g, '');
    }
});

signupLogin.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_\-]+$/.test(signupLogin.value)) {
        signupLogin.value = signupLogin.value.replace(/[^a-zA-Z0-9_\-]/g, '');
    }
});

signupPassword.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_.\-!]+$/.test(signupPassword.value)) {
        signupPassword.value = signupPassword.value.replace(/[^a-zA-Z0-9_.\-!]/g, '');
    }
});

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
            if (data.data.is_teacher) {
                window.location.href = "/teachers";
            } else {
                window.location.href = "/schoolchildren";
            }
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
            if (data.data.is_teacher) {
                window.location.href = "/teachers";
            } else {
                window.location.href = "/schoolchildren";
            }
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}
