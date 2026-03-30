// Set today's date in the header
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


updateDateTime();                        // run once immediately
setInterval(updateDateTime, 1000);


// Load attendance when page opens
loadAttendance();


let totalPresent = 0;



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
            }
        })
        .catch(() => showError("Failed to search attendance."));
}




function studentList(){
    const first_name = document.getElementById("search-first-name").value;
    const last_name = document.getElementById("search-last-name").value;
    const number = document.getElementById("search-number").value;

    let url = `/attendance/student_list?`;

    if (first_name)
        url += `first_name=${encodeURIComponent(first_name)}&`;

    if (last_name)
        url += `last_name=${encodeURIComponent(last_name)}&`;

    if (number)
        url += `student_number=${encodeURIComponent(number)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNoRecords();
            } else {
                listAll(data);
            }
        })
        .catch(() => showError("Failed to load student list."));
}



function listAll(studentList){
    const tbody = document.getElementById("student-body");
    const table = document.getElementById("student-table");

    tbody.innerHTML = "";
    table.classList.remove("hidden");

    studentList.forEach(student =>{
    tbody.innerHTML += `
            <tr>
                <td>${student.student_number}</td>
                <td>${student.first_name}</td>
                <td>${student.last_name}</td>
             <td>
                <button onclick="selectStudent('${student.student_number}')">
                    Select
                </button>
            </td>
            </tr>
        `;
    });
}



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
    const tbody = document.getElementById("verify-body");
    const table = document.getElementById("verify-table");

    tbody.innerHTML = "";
    table.classList.remove("hidden");

    tbody.innerHTML = `
        <tr>
            <td>${student.student_number}</td>
            <td>${student.first_name}</td>
            <td>${student.last_name}</td>
            <td>
                <button onclick="confirmAttendance('${student_number}')">Yes</button>
            </td>
            <td>
                <button onclick="cancelAttendance()">Cancel</button>
            </td>
        </tr>
    `;
}



function confirmAttendance(student_number) {
    fetch("/manual-log", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ student_number: student_number })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        cancelAttendance();
        loadAttendance()
    })
    .catch(() => showError("Failed to record attendance."));
}


function cancelAttendance() {
    const table = document.getElementById("verify-table");
    const tbody = document.getElementById("verify-body");
    tbody.innerHTML = "";
    table.classList.add("hidden");
}





// ─── Render table ─────────────────────────────────────────────────────────────

function renderTable(records, isFiltered = false) {
    const tbody = document.getElementById("attendance-body");
    const table = document.getElementById("attendance-table");
    const noRecords = document.getElementById("no-records");

    tbody.innerHTML = "";
    table.classList.remove("hidden");
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






// ─── Helper functions ─────────────────────────────────────────────────────────

function showNoRecords() {
    document.getElementById("attendance-body").innerHTML = "";
    document.getElementById("attendance-table").classList.add("hidden");
    document.getElementById("no-records").classList.remove("hidden");
    document.getElementById("total-count").textContent = 0;
    document.getElementById("timed-out-count").textContent = 0;
    document.getElementById("still-in-count").textContent = 0;
}



function showError(message) {
    const el = document.getElementById("status-message");
    el.textContent = message;
    el.className = "status-message status-error";
    setTimeout(() => el.classList.add("hidden"), 3000);
}


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
                totalPresent = data.length; // still save the real total
                const stillInOnly = data.filter(record => !record.time_out);
                if (stillInOnly.length === 0) {
                    showNoRecords();
                } else {
                    renderTable(stillInOnly, true); // pass true = is filtered
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