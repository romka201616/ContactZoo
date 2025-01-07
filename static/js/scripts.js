document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const toggleToRegister = document.getElementById("toggle-to-register");
    const toggleToLogin = document.getElementById("toggle-to-login");
    const formTitle = document.getElementById("form-title");

    if (toggleToRegister) {
        toggleToRegister.addEventListener("click", function (event) {
            event.preventDefault();
            loginForm.style.display = "none";
            registerForm.style.display = "block";
            toggleToRegister.style.display = "none";
            toggleToLogin.style.display = "inline";
            formTitle.textContent = "Регистрация";
        });
    }

    if (toggleToLogin) {
        toggleToLogin.addEventListener("click", function (event) {
            event.preventDefault();
            loginForm.style.display = "block";
            registerForm.style.display = "none";
            toggleToRegister.style.display = "inline";
            toggleToLogin.style.display = "none";
            formTitle.textContent = "Вход в систему";
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", function (event) {
            const username = document.getElementById("register-username").value.trim();
            const password = document.getElementById("register-password").value;
            const passwordConfirm = document.getElementById("register-password-confirm").value;
            const errorElement = document.getElementById("register-error");
            let errorMessage = "";

            if (username.length < 4) {
                errorMessage = "Имя пользователя должно содержать минимум 4 символа.";
            } else if (!/^[a-zA-Z0-9]+$/.test(username)) {
                errorMessage = "Имя пользователя должно содержать только цифры и буквы английского алфавита.";
            } else if (password.length < 8) {
                errorMessage = "Пароль должен содержать минимум 8 символов.";
            } else if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
                errorMessage = "Пароль должен содержать как минимум 1 букву и 1 цифру.";
            } else if (password !== passwordConfirm) {
                errorMessage = "Пароль и повтор пароля должны совпадать.";
            }

            if (errorMessage) {
                event.preventDefault();
                errorElement.textContent = errorMessage;
            } else {
                errorElement.textContent = "";
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            const username = document.getElementById("login-username").value.trim();
            const password = document.getElementById("login-password").value;
            const errorElement = document.getElementById("login-error");
            let errorMessage = "";

            if (!username || !password) {
                errorMessage = "Логин и пароль должны быть верными.";
            }

            if (errorMessage) {
                event.preventDefault();
                errorElement.textContent = errorMessage;
            } else {
                errorElement.textContent = "";
            }
        });
    }

    document.querySelectorAll("button.delete-button").forEach(function (button) {
        button.addEventListener("click", function (event) {
            const confirmDelete = confirm("Вы действительно хотите удалить запись?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    const addContactForm = document.querySelector("form");
    if (addContactForm) {
        addContactForm.addEventListener("submit", function (event) {
            let isValid = true;
            const nameField = document.getElementById("name");
            const surnameField = document.getElementById("surname");
            const phoneField = document.getElementById("phone");
            const photoField = document.getElementById("photo");

            if (!nameField.value.trim()) {
                isValid = false;
                nameField.classList.add("error-border");
            } else {
                nameField.classList.remove("error-border");
            }

            if (!surnameField.value.trim()) {
                isValid = false;
                surnameField.classList.add("error-border");
            } else {
                surnameField.classList.remove("error-border");
            }

            if (!phoneField.value.trim()) {
                isValid = false;
                phoneField.classList.add("error-border");
            } else {
                phoneField.classList.remove("error-border");
            }

            if (!photoField.value) {
                isValid = false;
                photoField.classList.add("error-border");
            } else {
                photoField.classList.remove("error-border");
            }

            if (!isValid) {
                alert("Не все поля заполнены");
                event.preventDefault();
            }
        });
    }

    document.querySelectorAll("button, .btn").forEach(function (button) {
        button.addEventListener("mouseover", function () {
            button.style.transform = "scale(1.05)";
            button.style.transition = "transform 0.2s";
        });

        button.addEventListener("mouseout", function () {
            button.style.transform = "scale(1)";
        });
    });
});