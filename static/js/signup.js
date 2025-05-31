let login = document.getElementById('login'),
    password = document.getElementById('password'),
    passwordRepeat = document.getElementById('passwordRepeat'),
    role = document.getElementById('role'),
    signupLogin = document.getElementById('signupLogin'),
    signupPassword = document.getElementById('signupPassword'),
    signupPasswordRepeat = document.getElementById('signupPasswordRepeat'),
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

passwordRepeat.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_.\-!]+$/.test(passwordRepeat.value)) {
        passwordRepeat.value = passwordRepeat.value.replace(/[^a-zA-Z0-9_.\-!]/g, '');
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

signupPasswordRepeat.addEventListener('input', function() {
    if (!/^[a-zA-Z0-9_.\-!]+$/.test(signupPasswordRepeat.value)) {
        signupPasswordRepeat.value = signupPasswordRepeat.value.replace(/[^a-zA-Z0-9_.\-!]/g, '');
    }
});

function signup_user() {
    if (signupPassword.value !== signupPasswordRepeat.value) {
        show_error('Пароли не совпадают!', 'Уведомление');
    } else {
        sendRequest(
            'POST',
            '/api/signup',
            true,
            {
                "phone_number": phoneNumber.value,
                "fio": fio.value.trim(),
                "birthday": (year.value+'-'+month.value+'-'+day.value),
                "gender": gender.value,
                "role": role.value,
                "login": signupLogin.value.trim(),
                "password": signupPassword.value.trim()
            },
            function (data) {
                console.log(data);
                let is_teacher = data.data.is_teacher;
                localStorage.setItem("is_teacher", is_teacher);
                if (is_teacher) {
                    window.location.href = "/teachers";
                } else {
                    window.location.href = "/schoolchildren";
                }
            },
            function (data) {
                console.log(data)
                show_error(data.message, 'Уведомление');
            }
        )
    }
}

function login_user() {
    if (password.value !== passwordRepeat.value) {
        show_error('Пароли не совпадают!', 'Уведомление');
    } else {
        sendRequest(
            'POST',
            '/api/login',
            true,
            {
                "login": login.value.trim(),
                "password": password.value.trim()
            },
            function (data) {
                console.log(data);
                let is_teacher = data.data.is_teacher;
                localStorage.setItem("is_teacher", is_teacher);
                if (is_teacher) {
                    window.location.href = "/teachers";
                } else {
                    window.location.href = "/schoolchildren";
                }
            },
            function (data) {
                console.log(data)
                show_error(data.message, 'Уведомление');
            }
        )
    }
}

function redirectUserByRole() {
    let is_teacher = localStorage.getItem("is_teacher");
    if (is_teacher === null) {
        console.log("is_teacher", is_teacher);
    } else {
        if (is_teacher === "true") {
            window.location.href = "/teachers";
        } else {
            window.location.href = "/schoolchildren";
        }
    }
}
