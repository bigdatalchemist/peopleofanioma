document.addEventListener("DOMContentLoaded", function () {
  const toggleButtons = document.querySelectorAll("[data-toggle='password']");

  toggleButtons.forEach(button => {
    const inputId = button.getAttribute("data-target");
    const input = document.getElementById(inputId);
    const icon = button.querySelector("svg");

    button.addEventListener("click", () => {
      if (input.type === "password") {
        input.type = "text";
        icon.innerHTML = `
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7
                   a9.99 9.99 0 012.184-3.356M6.18 6.18l11.64 11.64M10.12 10.12a3 3 0
                   004.24 4.24" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 00-3-3m0 0a3 3 0 00-3 3m6 0a3 3 0 01-6 0" />`;
      } else {
        input.type = "password";
        icon.innerHTML = `
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 
                   9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 
                   0-8.268-2.943-9.542-7z" />`;
      }
    });
  });
});
