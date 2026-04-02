function filterTasks() {
    let category = document.getElementById("filterCategory").value.toLowerCase();
    let priority = document.getElementById("filterPriority").value;
    let status = document.getElementById("filterStatus").value;

    document.querySelectorAll("#taskTable tbody tr[data-id]").forEach(row => {

        let rowCategory = row.children[2].innerText.toLowerCase();
        let rowPriority = row.children[7].innerText;
        let checkbox = row.querySelector(".toggle");

        let rowStatus = checkbox.checked ? "1" : "0";

        let show = true;

        if (category && !rowCategory.includes(category)) show = false;
        if (priority && rowPriority !== priority) show = false;
        if (status && rowStatus !== status) show = false;

        row.style.display = show ? "" : "none";
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
        .then(() => row.remove());
    });
});


// TOGGLE TASK
document.querySelectorAll(".toggle").forEach(box => {
    box.addEventListener("change", function() {
        let row = this.closest("tr");
        let id = row.dataset.id;

        fetch(`/toggle/${id}`, {method: "POST"});
    });
});

// FILTER
document.querySelectorAll(".filters input, .filters select")
.forEach(el => {
    el.addEventListener("input", filterTasks);
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
