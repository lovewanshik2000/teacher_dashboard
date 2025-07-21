document.getElementById("studentForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const name = document.getElementById("id_name").value;
    const subject = document.getElementById("id_subject").value;
    const marks = document.getElementById("id_marks").value;
  
    fetch("/add-student/", {
      method: "POST",
      headers: {"Content-Type": "application/json", "X-CSRFToken": getCSRFToken()},
      body: JSON.stringify({name, subject, marks})
    }).then(() => location.reload());
  });
  
  function updateStudent(id) {
    const row = document.querySelector(`tr[data-id='${id}']`);
    const name = row.children[0].innerText;
    const subject = row.children[1].innerText;
    const marks = row.children[2].innerText;
  
    fetch(`/update-student/${id}/`, {
      method: "POST",
      headers: {"Content-Type": "application/json", "X-CSRFToken": getCSRFToken()},
      body: JSON.stringify({name, subject, marks})
    }).then(() => alert("Updated!"));
  }
  
  function deleteStudent(id) {
    if (!confirm("Delete this student?")) return;
    fetch(`/delete-student/${id}/`, {
      method: "POST",
      headers: {"X-CSRFToken": getCSRFToken()}
    }).then(() => location.reload());
  }
  
  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
  