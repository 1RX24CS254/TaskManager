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


// ADD SUBTASK
function addSubtask(parentId, btn) {
    let input = btn.previousElementSibling;

    fetch(`/add_subtask/${parentId}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title: input.value})
    }).then(() => location.reload());
}


// FILTER
document.querySelectorAll(".filters input, .filters select")
.forEach(el => {
    el.addEventListener("input", filterTasks);
});

function filterTasks() {
    let category = document.getElementById("filterCategory")?.value.toLowerCase() || "";
    let priority = document.getElementById("filterPriority")?.value || "";

    document.querySelectorAll("#taskTable tbody tr").forEach(row => {
        let text = row.innerText.toLowerCase();

        let show = true;

        if (category && !text.includes(category)) show = false;
        if (priority && !text.includes(priority)) show = false;

        row.style.display = show ? "" : "none";
    });
}

});
