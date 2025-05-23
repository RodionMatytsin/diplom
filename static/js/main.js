function show_error(body, title) {
    let alert = document.getElementById('alert'),
        notice_title = document.getElementById('notice_title'),
        notice_text = document.getElementById('notice_text');
    alert.style.display = 'flex';
    notice_title.innerHTML = title;
    notice_text.innerHTML = body;
}

[].forEach.call( document.querySelectorAll('.tel'), function(input) {
    var keyCode;
    function mask(event) {
        event.keyCode && (keyCode = event.keyCode);
        var pos = this.selectionStart;
        if (pos < 3) event.preventDefault();
        var matrix = "+7 (___) ___ ____",
            i = 0,
            def = matrix.replace(/\D/g, ""),
            val = this.value.replace(/\D/g, ""),
            new_value = matrix.replace(/[_\d]/g, function(a) {
                return i < val.length ? val.charAt(i++) || def.charAt(i) : a
            });
        i = new_value.indexOf("_");
        if (i !== -1) {
            i < 5 && (i = 3);
            new_value = new_value.slice(0, i)
        }
        var reg = matrix.substr(0, this.value.length).replace(/_+/g,
            function(a) {
                return "\\d{1," + a.length + "}"
            }).replace(/[+()]/g, "\\$&");
        reg = new RegExp("^" + reg + "$");
        if (!reg.test(this.value) || this.value.length < 5 || keyCode > 47 && keyCode < 58) this.value = new_value;
        if (event.type === "blur" && this.value.length < 5)  this.value = ""
    }
    input.addEventListener("input", mask, false);
    input.addEventListener("focus", mask, false);
    input.addEventListener("blur", mask, false);
    input.addEventListener("keydown", mask, false)
});

function sendRequest(method, url, async=true, responses_data, onsuccess, onerror=function(){}) {
    let request = new XMLHttpRequest();
    request.open(method, url, async);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    request.onload = function () {
        let responseObj = JSON.parse(request.response);
        console.log(method, url, responseObj);
        if (request.status === 401) {
            window.location.href = "/";
        } else if (request.status >= 400) {
            show_error(responseObj.message, 'Ошибка');
        } else {
            if (responseObj.result === true) {
                onsuccess(responseObj);
            } else {
                onerror(responseObj);
            }
        }
    };

    request.onloadstart = function () {
        show_error('Подождите чуть-чуть...', 'Загрузка');
    };

    request.onprogress = function () {
        show_error('Подождите чуть-чуть...', 'Загрузка');
    };

    request.onreadystatechange = function () {
        if (this.readyState !== 4) {
            show_error('Подождите чуть-чуть...', 'Загрузка');
        } else {
            document.getElementById('alert').style.display = 'none';
        }
    };

    request.onerror = function () {
        show_error('Не предвиденная ошибка, перезагрузите страницу', 'Ошибка');
    };

    request.ontimeout = function () {
        show_error('Не предвиденная ошибка, перезагрузите страницу', 'Ошибка');
    };

    request.onabort = function () {
        show_error('Не предвиденная ошибка, перезагрузите страницу', 'Ошибка');
    };

    if (responses_data != null) {
        request.send(JSON.stringify(responses_data));
    } else {
        request.send();
    }
}

function openModal(src) {
    document.getElementById("modal").style.display = "flex";
    document.getElementById("modal_img").src = src;
}

function populateYearSelect() {
    const select = document.getElementById('year');
    const defaultYear = 2003;
    for (let year = 1944; year <= 2025; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === defaultYear) {
            option.selected = true;
        }
        select.appendChild(option);
    }
}
