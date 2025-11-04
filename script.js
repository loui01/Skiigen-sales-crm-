const currentYear = document.getElementById("year");
if (currentYear) {
  currentYear.textContent = new Date().getFullYear();
}

const modal = document.getElementById("account-modal");
const createAccountTriggers = document.querySelectorAll('[data-trigger="create-account"]');
const closeModalTrigger = document.querySelector('[data-trigger="close-modal"]');
const scrollLoginTriggers = document.querySelectorAll('[data-trigger="scroll-login"]');

function openModal() {
  if (modal) {
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
}

function closeModal() {
  if (modal) {
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
}

createAccountTriggers.forEach((trigger) => {
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    openModal();
  });
});

if (closeModalTrigger) {
  closeModalTrigger.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });
}

if (modal) {
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
}

scrollLoginTriggers.forEach((trigger) => {
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    document.getElementById("login")?.scrollIntoView({ behavior: "smooth" });
  });
});

const demoTrigger = document.querySelector('[data-trigger="request-demo"]');
if (demoTrigger) {
  demoTrigger.addEventListener("click", (event) => {
    event.preventDefault();
    openModal();
  });
}

const forms = document.querySelectorAll("form");
forms.forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const role = form.closest("article")?.querySelector("h3")?.textContent || "Account";
    alert(`${role} login is not connected yet. We\'ll route you once authentication is ready.`);
  });
});

const accountForm = modal?.querySelector("form");
accountForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  alert("Thanks! Our team will reach out with access instructions.");
  closeModal();
});
