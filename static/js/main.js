document.addEventListener("DOMContentLoaded", () => {

    /* ---------------- TOGGLE PANELS ---------------- */
    const taskBtn = document.getElementById("toggleTaskBtn");
    const filterBtn = document.getElementById("toggleFilterBtn");

    const taskPanel = document.getElementById("taskPanel");
    const filterPanel = document.getElementById("filterPanel");

    taskBtn?.addEventListener("click", () => {
        taskPanel.classList.toggle("hidden");
        filterPanel.classList.add("hidden");
    });

    filterBtn?.addEventListener("click", () => {
        filterPanel.classList.toggle("hidden");
        taskPanel.classList.add("hidden");
    });


    /* ---------------- ADD TASK ---------------- */
    document.getElementById("taskForm")?.addEventListener("submit", function(e) {
        e.preventDefault();

        let title = document.getElementById("title").value.trim();
        if (!title) return alert("Task title required");

        let category = document.getElementById("category").value;
        let priority = document.getElementById("priority").value;
        let due_date = document.getElementById("due_date").value;
        let description = document.getElementById("description").value;

        fetch("/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ title, category, priority, due_date, description })
        }).then(() => location.reload());
    });


    /* ---------------- ADD SUBTASK ---------------- */
    window.addSubtask = function(parentId, btn) {
        let container = btn.parentElement;

        let title = container.querySelector(".sub-title").value.trim();
        let category = container.querySelector(".sub-category").value;
        let priority = container.querySelector(".sub-priority").value;

        if (!title) {
            alert("Subtask title required");
            return;
        }

        fetch(`/add_subtask/${parentId}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ title, category, priority })
        }).then(() => location.reload());
    };


    /* ---------------- DELETE TASK ---------------- */
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("delete")) {

            if (!confirm("Delete this task?")) return;

            let row = e.target.closest("tr");
            let id = row.dataset.id;

            fetch(`/delete/${id}`, {method: "DELETE"})
            .then(() => {
                let subRow = row.nextElementSibling;

                row.remove();

                if (subRow && subRow.classList.contains("subtask-row")) {
                    subRow.remove();
                }
            });
        }
    });


    /* ---------------- DELETE SUBTASK ---------------- */
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("sub-delete")) {

            let sub = e.target.closest(".subtask");
            let id = sub.dataset.id;

            fetch(`/delete_subtask/${id}`, {method: "DELETE"})
            .then(() => sub.remove());
        }
    });


    /* ---------------- TOGGLE (TASK + SUBTASK) ---------------- */
    document.addEventListener("change", function(e) {
        if (e.target.classList.contains("toggle")) {

            let container = e.target.closest("tr") || e.target.closest(".subtask");
            let id = container?.dataset.id;

            if (!id) return;

            fetch(`/toggle/${id}`, {method: "POST"})
            .then(() => location.reload()); // keep state consistent
        }
    });


    /* ---------------- EDIT TASK ---------------- */
    document.querySelectorAll(".editable").forEach(cell => {
        cell.addEventListener("blur", function () {
            let row = this.closest("tr");
            let id = row.dataset.id;
            let field = this.dataset.field;
            let value = this.innerText.trim();

            fetch(`/edit/${id}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({field, value})
            });
        });
    });


    /* ---------------- EDIT SUBTASK ---------------- */
    document.addEventListener("blur", function(e) {
        if (e.target.classList.contains("sub-edit")) {

            let sub = e.target.closest(".subtask");
            let id = sub.dataset.id;
            let value = e.target.innerText.trim();

            fetch(`/edit_subtask/${id}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ field: "title", value })
            });
        }
    }, true);


    /* ---------------- FILTER TASKS ---------------- */
    function filterTasks() {
        let category = document.getElementById("filterCategory").value.toLowerCase().trim();
        let priority = document.getElementById("filterPriority").value.trim();
        let status = document.getElementById("filterStatus").value;

        document.querySelectorAll("#taskTable tbody tr[data-id]").forEach(row => {

            let show = true;

            let rowCategory = row.children[2].innerText.toLowerCase();
            let rowPriority = row.children[7].innerText.trim();

            // 🔥 use progress instead of checkbox
            let progressText = row.children[6].innerText;
            let percent = parseInt(progressText);

            let rowStatus = "0";
            if (percent === 100) rowStatus = "1";
            else if (percent > 0) rowStatus = "partial";

            if (category && !rowCategory.includes(category)) show = false;
            if (priority && rowPriority !== priority) show = false;
            if (status && rowStatus !== status) show = false;

            row.style.display = show ? "" : "none";

            let subRow = row.nextElementSibling;
            if (subRow && subRow.classList.contains("subtask-row")) {
                subRow.style.display = show ? "" : "none";
            }
        });
    }


    /* ---------------- FILTER EVENTS ---------------- */
    let debounce;
    document.querySelectorAll(".filters input, .filters select")
    .forEach(el => {
        el.addEventListener("input", () => {
            clearTimeout(debounce);
            debounce = setTimeout(filterTasks, 200);
        });

        el.addEventListener("change", filterTasks);
    });
    
    /*-----------RBAC----------------*/
    window.assignRole = function(taskId, select) {
    const role = select.value;

    fetch('/assign_role', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ task_id: taskId, role: role })
    })
    .then(res => res.json())
    .then(console.log);
}

});

function grantAccess(taskId, btn) {
    const row = btn.closest('tr');
    const role = row.querySelector('.dac-role').value;
    fetch('/grant_access', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({task_id: taskId, role: role, can_view:1, can_edit:1, can_delete:0})
    }).then(res => res.json()).then(console.log);
}

