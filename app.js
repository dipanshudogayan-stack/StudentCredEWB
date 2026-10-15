const form = document.getElementById("student-form");
const idInput = document.getElementById("student-id");
const body = document.getElementById("students-body");
const message = document.getElementById("message");
const searchInput = document.getElementById("search");
const saveButton = document.getElementById("save-button");
const cancelButton = document.getElementById("cancel-button");
const formTitle = document.getElementById("form-title");

const FIELDS = ["name", "email", "date_of_birth", "phone", "course", "enrollment_date", "address"];

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const err = await response.json();
      if (typeof err.detail === "string") detail = err.detail;
      else if (Array.isArray(err.detail)) {
        detail = err.detail.map(e => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join("; ");
      }
    } catch (_) {}
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function showMessage(text, type = "ok") {
  message.textContent = text;
  message.className = type;
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formData() {
  const data = {};
  for (const f of FIELDS) {
    const value = document.getElementById(f).value.trim();
    // Required fields are always sent; optional empty fields become null.
    data[f] = value === "" ? null : value;
  }
  return data;
}

async function loadStudents() {
  const term = searchInput.value.trim();
  const url = term ? `/students?search=${encodeURIComponent(term)}` : "/students";
  try {
    const students = await request(url);
    renderStudents(students);
  } catch (err) {
    showMessage(err.message, "error");
  }
}

function renderStudents(students) {
  if (students.length === 0) {
    body.innerHTML = `<tr><td colspan="9" class="empty">No students found.</td></tr>`;
    return;
  }
  body.innerHTML = students.map(s => `
    <tr>
      <td>${s.id}</td>
      <td>${escapeHtml(s.name)}</td>
      <td>${escapeHtml(s.date_of_birth)}</td>
      <td>${escapeHtml(s.email)}</td>
      <td>${escapeHtml(s.phone)}</td>
      <td>${escapeHtml(s.course)}</td>
      <td>${escapeHtml(s.address)}</td>
      <td>${escapeHtml(s.enrollment_date)}</td>
      <td class="actions-cell">
        <button class="small" data-action="edit" data-id="${s.id}">Edit</button>
        <button class="small danger" data-action="delete" data-id="${s.id}">Delete</button>
      </td>
    </tr>`).join("");
}

function resetForm() {
  form.reset();
  idInput.value = "";
  formTitle.textContent = "Add student";
  saveButton.textContent = "Add student";
  cancelButton.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = idInput.value;
  const url = id ? `/students/${id}` : "/students";
  const method = id ? "PATCH" : "POST";
  try {
    await request(url, { method, body: JSON.stringify(formData()) });
    showMessage(id ? "Student updated." : "Student added.");
    resetForm();
    await loadStudents();
  } catch (err) {
    showMessage(err.message, "error");
  }
});

cancelButton.addEventListener("click", () => {
  resetForm();
  showMessage("");
});

body.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;

  if (button.dataset.action === "edit") {
    try {
      const s = await request(`/students/${id}`);
      for (const f of FIELDS) document.getElementById(f).value = s[f] ?? "";
      idInput.value = s.id;
      formTitle.textContent = `Edit student #${s.id}`;
      saveButton.textContent = "Save changes";
      cancelButton.hidden = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      showMessage(err.message, "error");
    }
  } else if (button.dataset.action === "delete") {
    if (!confirm("Delete this student? This cannot be undone.")) return;
    try {
      await request(`/students/${id}`, { method: "DELETE" });
      showMessage("Student deleted.");
      if (idInput.value === id) resetForm();
      await loadStudents();
    } catch (err) {
      showMessage(err.message, "error");
    }
  }
});

let searchTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadStudents, 300);
});

loadStudents();
