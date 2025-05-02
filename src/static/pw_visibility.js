function togglePasswordVisibility() {
  const passwordInput = document.getElementById('password');
  const toggleButton = document.querySelector('.toggle-password, [onclick*=togglePasswordVisibility]');

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleButton.innerHTML = '&#9675;';
  } else {
    passwordInput.type = 'password';
    toggleButton.innerHTML = '&#9679;';
  }
}