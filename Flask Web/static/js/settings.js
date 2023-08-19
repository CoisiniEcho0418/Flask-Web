const newPassword = document.getElementById("new_password");
const confirmNewPassword = document.getElementById("confirm_new_password");
const passwordHelp = document.getElementById("passwordHelp");
const confirmPasswordHelp = document.getElementById("confirmPasswordHelp");

newPassword.addEventListener("input", function() {
    if (newPassword.value.length < 6) {
        passwordHelp.style.color = "red"; // 设置文本颜色为红色
        confirmPasswordHelp.innerText = "密码必须至少包含 6 个字符。";

    } else {
        confirmPasswordHelp.innerText = "";
    }
    updateConfirmPasswordHelp();
});

confirmNewPassword.addEventListener("input", function() {
    if (confirmNewPassword.value !== newPassword.value) {
        confirmPasswordHelp.style.color = "red"; // 设置文本颜色为红色
        confirmPasswordHelp.innerText = "前后密码不匹配。";

    } else {
        confirmPasswordHelp.innerText = "";
    }
});

function updateConfirmPasswordHelp() {
    if (confirmNewPassword.value !== "") {
        if (confirmNewPassword.value !== newPassword.value) {
            confirmPasswordHelp.innerText = "密码不匹配。";
            confirmPasswordHelp.style.color = "red"; // 设置文本颜色为红色
        } else {
            confirmPasswordHelp.innerText = "";
        }
    }
}