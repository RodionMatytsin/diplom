const key = "kAlu7NqZwoWx7MaRwoXv9Qc4woZnAp==";
const main = document.getElementById("main");
let name_class = document.getElementById('name_class');

main.addEventListener('click', () => {
    get_classes();
});

name_class.addEventListener('input', function() {
    if (!/^[a-zA-ZА-Яа-я0-9_+=\s]*$/.test(name_class.value)) {
        name_class.value = name_class.value.replace(/[^a-zA-ZА-Яа-я0-9_+=\s]/g, '');
    }
});

function add_class() {
    sendRequest(
        'POST',
        `/api/admin/classes?key=${key}`,
        true,
        {
            "name_class": name_class.value.trim()
        },
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_classes();
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data)
            show_error(data.message, 'Ошибка');
        }
    )
}

function del_class(class_guid) {
    sendRequest(
        'DELETE',
        `/api/admin/classes/${class_guid}?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            setTimeout(() => {
                get_classes();
            }, 500);
            show_error(data.message, 'Оповещение');
        },
        function (data) {
            console.log(data);
            show_error(data.message, 'Ошибка');
        }
    )
}

function create_class_for_dom(
    class_guid,
    name_class
) {
   let div_class = document.createElement('div'),
       div_class_about = document.createElement('div'),
       div_name_class = document.createElement('div'),
       div_del_class = document.createElement('div');

   div_class.id = class_guid;
   div_class.className = 'class_';
   div_class.appendChild(div_class_about);

   div_class_about.className = 'class_about';

   div_class_about.appendChild(div_name_class);
   div_name_class.className = 'name_class';
   div_name_class.innerHTML = '<b>Класс: </b>' + name_class;
   div_name_class.onclick = function () {
       show_error(class_guid, 'Оповещение');
   };

   div_class_about.appendChild(div_del_class);
   div_del_class.className = 'del_class';
   div_del_class.innerHTML = '+';
   div_del_class.onclick = function () {
       del_class(class_guid);
   };

   return div_class
}

function get_classes() {
    let classes_list = document.getElementById('classes_list');
    classes_list.innerHTML = '';
    sendRequest(
        'GET',
        `/api/admin/classes?key=${key}`,
        true,
        null,
        function (data) {
            console.log(data);
            let classes = data.data;
            if (classes.length === 0) {
                const classItem = document.createElement('div');
                classItem.classList.add('none_data');
                classItem.style.margin = '1% 0 0 0';
                classItem.style.fontSize = '2vw';
                classItem.innerHTML = 'Пока еще нет существующих классов ! :(';
                classes_list.appendChild(classItem);
            }else{
                for (let i = 0; i < classes.length; i++) {
                    classes_list.appendChild(
                        create_class_for_dom(
                            classes[i].guid,
                            classes[i].name
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