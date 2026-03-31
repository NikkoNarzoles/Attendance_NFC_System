// ─── Date / Time ─────────────────────────────────────────────────────────────

function updateDateTime() {
    document.getElementById("current-datetime").textContent =
        new Date().toLocaleString("en-PH", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true
        });
}

updateDateTime();
setInterval(updateDateTime, 1000);


// ─── Layer switching ──────────────────────────────────────────────────────────

function showLayer(className) {
    const layers = document.querySelectorAll('.first_layer, .second_layer, .third_layer');
    layers.forEach(layer => layer.classList.add("hidden"));

    const target = document.querySelector('.' + className);
    if (target) target.classList.remove("hidden");
}


// ─── State ────────────────────────────────────────────────────────────────────

let totalPresent = 0;
let selectedStudentNumber = null;


// ─── Load attendance by date and order ───────────────────────────────────────

function loadAttendance() {
    const order = document.getElementById("order-select").value;
    const date = document.getElementById("search-date").value;

    let url = `/attendance?order_clause=${order}`;
    if (date) url += `&at_date=${date}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNoRecords();
            } else {
                totalPresent = data.length;
                renderTable(data, false);
                showLayer('first_layer');
            }
        })
        .catch(() => showError("Failed to load attendance."));
}


// ─── Search attendance ────────────────────────────────────────────────────────

function searchAttendance() {
    const first_name = document.getElementById("search-first-name").value;
    const last_name = document.getElementById("search-last-name").value;
    const number = document.getElementById("search-number").value;
    const date = document.getElementById("search-date").value;
    const order = document.getElementById("order-select").value;

    let url = `/attendance/search?order_clause=${order}`;
    if (date) url += `&at_date=${date}`;
    if (number) url += `&student_number=${number}`;
    if (first_name) url += `&first_name=${first_name}`;
    if (last_name) url += `&last_name=${last_name}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNoRecords();
            } else {
                renderTable(data);
                showLayer('first_layer');
            }
        })
        .catch(() => showError("Failed to search attendance."));
}


// ─── Student list (Layer 2) ───────────────────────────────────────────────────

function studentList() {
    const first_name = document.getElementById("search-first-name").value;
    const last_name = document.getElementById("search-last-name").value;
    const number = document.getElementById("search-number").value;

    let url = `/attendance/student_list?`;
    if (first_name) url += `first_name=${encodeURIComponent(first_name)}&`;
    if (last_name) url += `last_name=${encodeURIComponent(last_name)}&`;
    if (number) url += `student_number=${encodeURIComponent(number)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showError("No students found.");
            } else {
                listAll(data);
                showLayer('second_layer'); // ← switch to layer 2 after data loads
            }
        })
        .catch(() => showError("Failed to load student list."));
}


function listAll(students) {
    const tbody = document.getElementById("student-body");
    tbody.innerHTML = "";

    students.forEach(student => {
        tbody.innerHTML += `
            <tr>
                <td>${student.student_number}</td>
                <td>${student.first_name}</td>
                <td>${student.last_name}</td>
                <td>
                    <button class="select" onclick="selectStudent('${student.student_number}')">
                        Select
                    </button>
                </td>
            </tr>
        `;
    });
}


// ─── Select student → Layer 3 ─────────────────────────────────────────────────

function selectStudent(student_number) {
    let url = `/attendance/student_list?student_number=${student_number}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showError("Cannot find student.");
            } else {
                addManualAttendance(data[0], student_number);
            }
        })
        .catch(() => showError("Cannot find student."));
}


function addManualAttendance(student, student_number) {
    selectedStudentNumber = student_number;

    const tbody = document.getElementById("verify-body");
    tbody.innerHTML = `
        <tr>
            <td>Student Number</td>
            <td>${student.student_number}</td>
        </tr>
        <tr>
            <td>First Name</td>
            <td>${student.first_name}</td>
        </tr>
        <tr>
            <td>Last Name</td>
            <td>${student.last_name}</td>
        </tr>
    `;

    showLayer('third_layer'); // ← switch to layer 3
}


// ─── Confirm / Cancel manual attendance ──────────────────────────────────────

function confirmAttendance() {
    if (!selectedStudentNumber) return;

    fetch("/manual-log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_number: selectedStudentNumber })
    })
    .then(response => response.json())
    .then(data => {
        selectedStudentNumber = null;
        showToast(data.message, "success");
        loadAttendance();
    })
    .catch(() => showToast("Failed to record attendance.", "error"));
}


// ─── Render attendance table ──────────────────────────────────────────────────

function renderTable(records, isFiltered = false) {
    const tbody = document.getElementById("attendance-body");
    const noRecords = document.getElementById("no-records");

    tbody.innerHTML = "";
    noRecords.classList.add("hidden");

    let timedOutCount = 0;
    let stillInCount = 0;

    records.forEach(record => {
        const isStillIn = !record.time_out;
        if (isStillIn) stillInCount++;
        else timedOutCount++;

        tbody.innerHTML += `
            <tr>
                <td>${record.student_number}</td>
                <td>${record.first_name} ${record.last_name}</td>
                <td>${record.at_date}</td>
                <td>${record.time_in}</td>
                <td>${record.time_out ?? "—"}</td>
                <td class="${isStillIn ? 'status-in' : 'status-out'}">
                    ${isStillIn ? "Still Inside" : "Timed Out"}
                </td>
            </tr>
        `;
    });

    document.getElementById("total-count").textContent = totalPresent;
    document.getElementById("timed-out-count").textContent = timedOutCount;
    document.getElementById("still-in-count").textContent = stillInCount;
}


// ─── Helper: no records ───────────────────────────────────────────────────────

function showNoRecords() {
    document.getElementById("attendance-body").innerHTML = "";
    document.getElementById("no-records").classList.remove("hidden");
    document.getElementById("total-count").textContent = 0;
    document.getElementById("timed-out-count").textContent = 0;
    document.getElementById("still-in-count").textContent = 0;
    showLayer('first_layer');
}


// ─── Toast notification system ────────────────────────────────────────────────

let toastTimer = null;

function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    const toastIcon = document.getElementById("toast-icon");
    const toastMsg = document.getElementById("toast-message");
    const toastBar = document.getElementById("toast-bar");

    // Clear any existing timer
    if (toastTimer) clearTimeout(toastTimer);

    // Set content
    toastMsg.textContent = message;
    toast.className = "toast toast-" + type;

    // Set icon
    if (type === "success") {
        toastIcon.innerHTML = `<i class="fa fa-check-circle"></i>`;
    } else {
        toastIcon.innerHTML = `<i class="fa fa-times-circle"></i>`;
    }

    // Show
    toast.classList.remove("toast-hidden");
    toast.classList.add("toast-visible");

    // Animate progress bar
    toastBar.style.transition = "none";
    toastBar.style.width = "100%";
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            toastBar.style.transition = "width 4s linear";
            toastBar.style.width = "0%";
        });
    });

    // Auto-dismiss after 4s
    toastTimer = setTimeout(() => dismissToast(), 4000);
}

function dismissToast() {
    const toast = document.getElementById("toast");
    toast.classList.remove("toast-visible");
    toast.classList.add("toast-hidden");
    if (toastTimer) {
        clearTimeout(toastTimer);
        toastTimer = null;
    }
}

// Keep old showError as alias so nothing breaks
function showError(message) {
    showToast(message, "error");
}


// ─── Filter: still inside ─────────────────────────────────────────────────────

function filterStillIn() {
    const order = document.getElementById("order-select").value;
    const date = document.getElementById("search-date").value;

    let url = `/attendance?order_clause=${order}`;
    if (date) url += `&at_date=${date}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNoRecords();
            } else {
                totalPresent = data.length;
                const stillInOnly = data.filter(record => !record.time_out);
                if (stillInOnly.length === 0) {
                    showNoRecords();
                } else {
                    renderTable(stillInOnly, true);
                    showLayer('first_layer');
                }
            }
        })
        .catch(() => showError("Failed to filter attendance."));
}


// ─── Button events ────────────────────────────────────────────────────────────

document.getElementById("search-btn").addEventListener("click", searchAttendance);

document.getElementById("student-list").addEventListener("click", studentList);

document.getElementById("reset-btn").addEventListener("click", () => {
    document.getElementById("search-first-name").value = "";
    document.getElementById("search-last-name").value = "";
    document.getElementById("search-number").value = "";
    document.getElementById("search-date").value = "";
    document.getElementById("order-select").value = "time_in_desc";
    loadAttendance();
});

document.getElementById("order-select").addEventListener("change", loadAttendance);
document.getElementById("still-in-btn").addEventListener("click", filterStillIn);
document.getElementById("show-all-btn").addEventListener("click", loadAttendance);
document.getElementById("search-date").addEventListener("click", function () { this.showPicker(); });

// Wire up the manual log confirm button
document.getElementById("manual-log-btn").addEventListener("click", confirmAttendance);

loadAttendance();