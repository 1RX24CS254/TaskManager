function filterTasks() {
    let category = document.getElementById("filterCategory").value.toLowerCase().trim();
    let priority = document.getElementById("filterPriority").value.trim();
    let status = document.getElementById("filterStatus").value;

    document.querySelectorAll("#taskTable tbody tr[data-id]").forEach(row => {

        let show = true;

        // safer extraction
        let rowCategory = row.children[2].innerText.trim().toLowerCase();
        let rowPriority = row.children[7].innerText.trim();
        let checkbox = row.querySelector(".toggle");
        let rowStatus = checkbox.checked ? "1" : "0";

        // category filter
        if (category && !rowCategory.includes(category)) show = false;

        // priority filter (loose match)
        if (priority && rowPriority !== priority) show = false;

        // status filter
        if (status && rowStatus !== status) show = false;

        row.style.display = show ? "" : "none";

        // hide/show subtask row
        let subRow = row.nextElementSibling;
        if (subRow && subRow.classList.contains("subtask-row")) {
            subRow.style.display = show ? "" : "none";
        }
    });
}


// ADD SUBTASK
function addSubtask(parentId, btn) {
    let container = btn.parentElement;

    let title = container.querySelector(".sub-title").value;
    let category = container.querySelector(".sub-category").value;
    let priority = container.querySelector(".sub-priority").value;

    fetch(`/add_subtask/${parentId}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title,
            category,
            priority
        })
    }).then(() => location.reload());
}


document.addEventListener("DOMContentLoaded", () => {

// ADD TASK
document.getElementById("taskForm")?.addEventListener("submit", function(e) {
    e.preventDefault();

    let title = document.getElementById("title").value;
    let category = document.getElementById("category").value;
    let priority = document.getElementById("priority").value;
    let due_date = document.getElementById("due_date").value;
    let description = document.getElementById("description").value;

    fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title,
            category,
            priority,
            due_date,
            description
        })
    }).then(() => location.reload());
});


// DELETE TASK
document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", function() {
        let row = this.closest("tr");
        let id = row.dataset.id;

        fetch(`/delete/${id}`, {method: "DELETE"})
        .then(() => {
            let subRow = row.nextElementSibling;
            row.remove();
            if (subRow && subRow.classList.contains("subtask-row")) {
                subRow.remove();
    }
});
    });
});


// TOGGLE TASK
document.querySelectorAll(".filters input, .filters select")
.forEach(el => {
    el.addEventListener("input", filterTasks);
});

// FILTER
document.addEventListener("change", function(e) {
    if (e.target.classList.contains("toggle")) {

        let container = e.target.closest("tr") || e.target.closest(".subtask");
        let id = container?.dataset.id;

        if (!id) return;

        fetch(`/toggle/${id}`, {method: "POST"});
    }
});

document.querySelectorAll(".editable").forEach(cell => {
    cell.addEventListener("blur", function () {
        let row = this.closest("tr");
        let id = row.dataset.id;
        let field = this.dataset.field;
        let value = this.innerText;

        fetch(`/edit/${id}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({field, value})
        });
    });
});

});
