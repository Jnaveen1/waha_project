const reportSearchInput =
    document.getElementById("reportSearchInput");

const reminderSearchInput =
    document.getElementById("reminderSearchInput");

const contactSearchInput = document.getElementById(
    "contactSearchInput"
);

const editingReportIdInput = document.getElementById(
    "editingReportId"
);

const saveReportButton = document.getElementById(
    "saveReportButton"
);

const cancelReportEditButton = document.getElementById(
    "cancelReportEditButton"
);

const summaryReminderCount = document.getElementById(
    "summaryReminderCount"
);

const openReportsButton = document.getElementById(
    "openReportsButton"
);

const closeReportsButton = document.getElementById(
    "closeReportsButton"
);

const reportsModal = document.getElementById(
    "reportsModal"
);

const reportForm = document.getElementById(
    "reportForm"
);

const reportNameInput = document.getElementById(
    "reportName"
);

const taskTitleInput = document.getElementById(
    "taskTitle"
);

const reportMessageInput = document.getElementById(
    "reportMessage"
);

const reportDetailsInput = document.getElementById(
    "reportDetails"
);

const reportManagementList = document.getElementById(
    "reportManagementList"
);

const reportManagementCount = document.getElementById(
    "reportManagementCount"
);

const summaryReportCount = document.getElementById(
    "summaryReportCount"
);

const reportSelect = document.getElementById(
    "reportSelect"
);

const selectedReportName = document.getElementById(
    "selectedReportName"
);

const selectedTaskTitle = document.getElementById(
    "selectedTaskTitle"
);

const selectedReportMessage = document.getElementById(
    "selectedReportMessage"
);

const selectedReportDetails = document.getElementById(
    "selectedReportDetails"
);

const scheduleTimeInput = document.getElementById(
    "scheduleTime"
);

let reports = [];

const openReminderFormButton = document.getElementById(
    "openReminderFormButton"
);

const closeReminderFormButton = document.getElementById(
    "closeReminderFormButton"
);

const cancelReminderButton = document.getElementById(
    "cancelReminderButton"
);

const reminderModal = document.getElementById("reminderModal");
const reminderForm = document.getElementById("reminderForm");

const contactList = document.getElementById("contactList");
const groupList = document.getElementById("groupList");

const repeatType = document.getElementById("repeatType");
const scheduleDateGroup = document.getElementById(
    "scheduleDateGroup"
);
const scheduleDate = document.getElementById("scheduleDate");

const weekDayGroup = document.getElementById("weekDayGroup");
const weekDay = document.getElementById("weekDay");

const recipientError = document.getElementById("recipientError");

const selectAllContactsButton = document.getElementById(
    "selectAllContactsButton"
);

const selectAllGroupsButton = document.getElementById(
    "selectAllGroupsButton"
);

const reminderTableBody = document.getElementById(
    "reminderTableBody"
);

const reminderCount = document.getElementById("reminderCount");

const contactNameInput = document.getElementById(
    "contactName"
);

const contactNumberInput = document.getElementById(
    "contactNumber"
);

const addContactButton = document.getElementById(
    "addContactButton"
);

let contacts = [];
let groups = [];
let reminders = [];
const selectedContactIds = new Set();

function openReminderModal() {
    reminderModal.classList.remove("hidden");
}

function closeReminderModal() {
    reminderModal.classList.add("hidden");

    reminderForm.reset();

    recipientError.classList.add("hidden");

    clearSelectedRecipients();

    updateScheduleFields();
}

function openReportsModal() {
    console.log("Opening reports modal");

    if (!reportsModal) {
        console.error("reportsModal element not found");
        return;
    }

    reportsModal.classList.remove("hidden");
}

function closeReportsModal() {
    if (!reportsModal) {
        return;
    }

    reportsModal.classList.add("hidden");
}

function createRecipientItem(recipient) {
    const item = document.createElement("label");

    item.className = "recipient-item";

    const checkbox = document.createElement("input");

    checkbox.type = "checkbox";
    checkbox.value = recipient.chat_id;
    checkbox.dataset.name =
        recipient.recipient_name;
    checkbox.dataset.type =
        recipient.recipient_type;

    const recipientDetails =
        document.createElement("span");

    recipientDetails.textContent =
        `${recipient.recipient_name} (${recipient.chat_id})`;

    item.appendChild(checkbox);
    item.appendChild(recipientDetails);

    return item;
}

function updateReportPreview() {
    const reportId = Number(reportSelect.value);

    const selectedReport = reports.find(
        (report) => report.id === reportId
    );

    if (!selectedReport) {
        selectedReportName.textContent =
            "No report selected";

        selectedTaskTitle.textContent =
            "Select a report to preview its task.";

        selectedReportMessage.textContent =
            "The saved report message will appear here.";

        selectedReportDetails.textContent = "";
        selectedReportDetails.classList.add("hidden");

        return;
    }

    selectedReportName.textContent =
        selectedReport.report_name;

    selectedTaskTitle.textContent =
        selectedReport.task_title;

    selectedReportMessage.textContent =
        selectedReport.message;

    if (selectedReport.details) {
        selectedReportDetails.textContent =
            selectedReport.details;

        selectedReportDetails.classList.remove(
            "hidden"
        );
    } else {
        selectedReportDetails.textContent = "";

        selectedReportDetails.classList.add(
            "hidden"
        );
    }
}

async function loadWhatsAppRecipients() {
    try {
        const response = await fetch(
            "/api/whatsapp/recipients"
        );

        const result = await response.json();

        console.log(
            "WhatsApp recipients:",
            result
        );

        if (!result.success) {
            alert(
                result.message ||
                "Unable to load WhatsApp recipients."
            );

            contacts = [];
            groups = [];

            loadContacts();
            loadGroups();

            return;
        }

        groups = result.groups || [];

        loadGroups();

    } catch (error) {
        console.error(
            "Load WhatsApp recipients error:",
            error
        );

        alert(
            "Unable to connect to WhatsApp service."
        );

        contacts = [];
        groups = [];

        loadContacts();
        loadGroups();
    }
}

async function loadSavedContacts() {
    try {
        const response = await fetch("/api/contacts");

        const result = await response.json();

        if (!result.success) {
            alert(
                result.message ||
                "Unable to load saved contacts."
            );

            contacts = [];
            loadContacts();

            return;
        }

        contacts = result.contacts || [];

        loadContacts();

    } catch (error) {
        console.error(
            "Load saved contacts error:",
            error
        );

        contacts = [];
        loadContacts();
    }
}

async function addSavedContact() {
    const name = contactNameInput.value.trim();
    const number = contactNumberInput.value.trim();

    if (!name) {
        alert("Contact name is required.");
        return;
    }

    if (!number) {
        alert("WhatsApp number is required.");
        return;
    }

    try {
        const response = await fetch(
            "/api/contacts",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    whatsapp_number: number
                })
            }
        );

        const result = await response.json();

        if (!result.success) {
            alert(
                result.message ||
                "Unable to save contact."
            );

            return;
        }

        contactNameInput.value = "";
        contactNumberInput.value = "";

        await loadSavedContacts();

        const newChatId = result.contact?.chat_id;

        if (newChatId) {
            const newCheckbox = contactList.querySelector(
                `input[value="${newChatId}"]`
            );

            if (newCheckbox) {
                newCheckbox.checked = true;
            }
        }

        alert("Contact saved successfully.");

    } catch (error) {
        console.error(
            "Save contact error:",
            error
        );

        alert("Unable to connect to the server.");
    }
}

async function handleReportSubmit(event) {
    event.preventDefault();

    const reportData = {
        report_name: reportNameInput.value.trim(),
        task_title: taskTitleInput.value.trim(),
        message: reportMessageInput.value.trim(),
        details: reportDetailsInput.value.trim() || null
    };

    const editingReportId =
        editingReportIdInput.value;

    const isEditing = Boolean(editingReportId);

    const url = isEditing
        ? `/api/reports/${editingReportId}`
        : "/api/reports";

    const method = isEditing
        ? "PUT"
        : "POST";

    try {
        const response = await fetch(
            url,
            {
                method: method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(reportData)
            }
        );

        const result = await response.json();

        if (!result.success) {
            alert(
                result.message ||
                "Unable to save report."
            );
            return;
        }

        resetReportForm();

        await loadReports();

        alert(
            isEditing
                ? "Report updated successfully."
                : "Report saved successfully."
        );

    } catch (error) {
        console.error(
            "Save report error:",
            error
        );

        alert("Unable to connect to the server.");
    }
}

function loadReportDropdown() {

    reportSelect.innerHTML = `
        <option value="">
            Select a report
        </option>
    `;

    reports.forEach((report) => {

        const option =
            document.createElement("option");

        option.value = report.id;

        option.textContent =
            report.report_name;

        reportSelect.appendChild(
            option
        );
    });
}

async function loadReports() {
    try {
        const response = await fetch("/api/reports");

        const result = await response.json();

        if (!result.success) {
            reports = [];
            renderReports();
            return;
        }

        reports = result.reports || [];

        loadReportDropdown();

        renderReports();

    } catch (error) {
        console.error(
            "Load reports error:",
            error
        );

        reports = [];
        renderReports();
    }
}

function renderReports(searchText = "") {

    reportManagementList.innerHTML = "";

    const search =
        searchText.trim().toLowerCase();

    const filteredReports = reports.filter(
        (report) => {

            const reportName =
                (report.report_name || "")
                    .toLowerCase();

            const taskTitle =
                (report.task_title || "")
                    .toLowerCase();

            const message =
                (report.message || "")
                    .toLowerCase();

            return (
                reportName.includes(search) ||
                taskTitle.includes(search) ||
                message.includes(search)
            );
        }
    );

    reportManagementCount.textContent =
        `${filteredReports.length} report${filteredReports.length === 1
            ? ""
            : "s"
        }`;

    if (filteredReports.length === 0) {

        reportManagementList.innerHTML = `
            <div class="empty-state">

                <div class="empty-state-icon">
                    ▤
                </div>

                <h4>
                    No matching reports
                </h4>

                <p>
                    Try another report name,
                    task title or message.
                </p>

            </div>
        `;

        return;
    }

    filteredReports.forEach((report) => {

        const card =
            document.createElement("article");

        card.className = "report-card";

        card.innerHTML = `
            <div class="report-card-header">

                <div>
                    <h4>
                        ${report.report_name}
                    </h4>

                    <span class="task-title">
                        ${report.task_title}
                    </span>
                </div>

            </div>

            <p class="report-message">
                ${report.message}
            </p>

            <div class="report-card-actions">

                <button
                    type="button"
                    class="edit-button"
                >
                    Edit
                </button>

                <button
                    type="button"
                    class="delete-button"
                >
                    Delete
                </button>

            </div>
        `;

        card
            .querySelector(".edit-button")
            .addEventListener(
                "click",
                () => {
                    startReportEdit(
                        report.id
                    );
                }
            );

        card
            .querySelector(".delete-button")
            .addEventListener(
                "click",
                () => {
                    deleteReport(
                        report.id
                    );
                }
            );

        reportManagementList.appendChild(
            card
        );
    });
}

function loadContacts(searchText = "") {
    contactList.innerHTML = "";

    const normalizedSearch =
        searchText.trim().toLowerCase();

    const filteredContacts = contacts.filter(
        (contact) => {
            const name =
                contact.name.toLowerCase();

            const number =
                contact.whatsapp_number.toLowerCase();

            return (
                name.includes(normalizedSearch) ||
                number.includes(normalizedSearch)
            );
        }
    );

    if (filteredContacts.length === 0) {
        contactList.innerHTML = `
            <p class="empty-message">
                No matching contacts found.
            </p>
        `;

        return;
    }

    filteredContacts.forEach((contact) => {
        const item =
            document.createElement("label");

        item.className = "recipient-item";

        const checkbox =
            document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.value = contact.chat_id;
        checkbox.dataset.name = contact.name;
        checkbox.dataset.type = "contact";

        checkbox.checked =
            selectedContactIds.has(
                contact.chat_id
            );

        checkbox.addEventListener(
            "change",
            () => {
                if (checkbox.checked) {
                    selectedContactIds.add(
                        contact.chat_id
                    );
                } else {
                    selectedContactIds.delete(
                        contact.chat_id
                    );
                }
            }
        );

        const details =
            document.createElement("span");

        details.textContent =
            `${contact.name} (${contact.whatsapp_number})`;

        item.appendChild(checkbox);
        item.appendChild(details);

        contactList.appendChild(item);
    });
}

function loadGroups() {
    groupList.innerHTML = "";

    if (groups.length === 0) {
        groupList.innerHTML = `
            <p class="empty-message">
                No WhatsApp groups found.
            </p>
        `;

        return;
    }

    groups.forEach((group) => {
        const item = createRecipientItem(
            group
        );

        groupList.appendChild(item);
    });
}

function clearSelectedRecipients() {
    selectedContactIds.clear();

    const allCheckboxes =
        document.querySelectorAll(
            '.recipient-list input[type="checkbox"]'
        );

    allCheckboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });

    selectAllContactsButton.textContent =
        "Select all";

    selectAllGroupsButton.textContent =
        "Select all";
}

function toggleAllRecipients(container, button) {
    const checkboxes = container.querySelectorAll(
        'input[type="checkbox"]'
    );

    const allSelected = Array.from(checkboxes).every(
        (checkbox) => checkbox.checked
    );

    checkboxes.forEach((checkbox) => {
        checkbox.checked = !allSelected;
    });

    button.textContent = allSelected
        ? "Select all"
        : "Clear all";
}

function updateScheduleFields() {
    const selectedRepeatType = repeatType.value;

    scheduleDateGroup.classList.add("hidden");
    weekDayGroup.classList.add("hidden");

    scheduleDate.required = false;
    weekDay.required = false;

    if (selectedRepeatType === "once") {
        scheduleDateGroup.classList.remove("hidden");
        scheduleDate.required = true;
    }

    if (selectedRepeatType === "weekly") {
        weekDayGroup.classList.remove("hidden");
        weekDay.required = true;
    }
}

function getSelectedRecipients() {
    const selectedRecipients = [];

    contacts.forEach((contact) => {
        if (
            selectedContactIds.has(
                contact.chat_id
            )
        ) {
            selectedRecipients.push({
                recipient_name: contact.name,
                chat_id: contact.chat_id,
                recipient_type: "contact"
            });
        }
    });

    const selectedGroupCheckboxes =
        groupList.querySelectorAll(
            'input[type="checkbox"]:checked'
        );

    selectedGroupCheckboxes.forEach(
        (checkbox) => {
            selectedRecipients.push({
                recipient_name:
                    checkbox.dataset.name,

                chat_id: checkbox.value,

                recipient_type:
                    checkbox.dataset.type
            });
        }
    );

    return selectedRecipients;
}

function formatSchedule(reminder) {
    if (reminder.repeatType === "once") {
        return `${reminder.scheduleDate} at ${reminder.scheduleTime}`;
    }

    if (reminder.repeatType === "daily") {
        return `Daily at ${reminder.scheduleTime}`;
    }

    return `${reminder.weekDay} at ${reminder.scheduleTime}`;
}

function createStatusBadge(status) {

    const badge =
        document.createElement("span");

    badge.style.padding = "5px 10px";
    badge.style.borderRadius = "12px";
    badge.style.fontSize = "13px";
    badge.style.fontWeight = "700";

    if (status === "active") {
        badge.textContent = "Active";

        badge.style.background =
            "#dcfce7";

        badge.style.color =
            "#166534";
    }

    else if (status === "inactive") {
        badge.textContent = "Inactive";

        badge.style.background =
            "#fee2e2";

        badge.style.color =
            "#991b1b";
    }

    else if (status === "completed") {
        badge.textContent = "Completed";

        badge.style.background =
            "#e0f2fe";

        badge.style.color =
            "#0369a1";
    }

    else if (status === "missed") {
        badge.textContent = "Missed";

        badge.style.background =
            "#fef3c7";

        badge.style.color =
            "#92400e";
    }

    else {
        badge.textContent = status || "Unknown";

        badge.style.background =
            "#f1f5f9";

        badge.style.color =
            "#475569";
    }

    return badge;
}

function renderReminders(searchText = "") {

    const search =
        searchText.trim().toLowerCase();

    const filteredReminders = reminders.filter(
        (reminder) => {

            const recipients =
                (reminder.recipients || [])
                    .map(
                        (recipient) =>
                            recipient.recipient_name
                    )
                    .join(" ")
                    .toLowerCase();

            const reportName =
                (
                    reminder.reportName ||
                    reminder.message ||
                    ""
                )
                    .toLowerCase();

            const schedule =
                formatSchedule(reminder)
                    .toLowerCase();

            return (
                reportName.includes(search) ||
                recipients.includes(search) ||
                schedule.includes(search)
            );
        }
    );


    reminderTableBody.innerHTML = "";


    reminderCount.textContent =
        `${filteredReminders.length} reminder${filteredReminders.length === 1
            ? ""
            : "s"
        }`;


    if (filteredReminders.length === 0) {

        reminderTableBody.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="empty-message"
                >
                    No matching reminders found.
                </td>
            </tr>
        `;

        return;
    }


    filteredReminders.forEach((reminder) => {

        const row =
            document.createElement("tr");


        // --------------------------------
        // Report / Message Column
        // --------------------------------

        const messageCell =
            document.createElement("td");

        const reportName =
            document.createElement("strong");

        reportName.textContent =
            reminder.reportName ||
            "Unnamed Report";

        messageCell.appendChild(
            reportName
        );


        if (reminder.taskTitle) {

            const taskTitle =
                document.createElement("small");

            taskTitle.className =
                "table-subtext";

            taskTitle.textContent =
                reminder.taskTitle;

            messageCell.appendChild(
                taskTitle
            );
        }


        // --------------------------------
        // Recipients Column
        // --------------------------------

        const recipientCell =
            document.createElement("td");

        recipientCell.textContent =
            (reminder.recipients || [])
                .map(
                    (recipient) =>
                        recipient.recipient_name
                )
                .join(", ");


        // --------------------------------
        // Schedule Column
        // --------------------------------

        const scheduleCell =
            document.createElement("td");

        scheduleCell.textContent =
            formatSchedule(reminder);


        // --------------------------------
        // Status Column
        // --------------------------------

        const statusCell =
            document.createElement("td");

        statusCell.appendChild(
            createStatusBadge(
                reminder.status
            )
        );


        // --------------------------------
        // Actions Column
        // --------------------------------

        const actionsCell =
            document.createElement("td");


        // Enable / Disable only if reminder is not completed

        if (
            reminder.status === "active" ||
            reminder.status === "inactive"
        ) {

            const toggleButton =
                document.createElement("button");

            toggleButton.type = "button";

            toggleButton.className =
                "text-button";

            toggleButton.textContent =
                reminder.status === "active"
                    ? "Disable"
                    : "Enable";

            toggleButton.addEventListener(
                "click",
                () => {
                    toggleReminderStatus(
                        reminder.id
                    );
                }
            );

            actionsCell.appendChild(
                toggleButton
            );
        }

        // Delete button always available

        const deleteButton =
            document.createElement("button");

        deleteButton.type = "button";

        deleteButton.className =
            "text-button";

        deleteButton.textContent =
            "Delete";

        deleteButton.style.marginLeft =
            "12px";

        deleteButton.style.color =
            "#dc3545";

        deleteButton.addEventListener(
            "click",
            () => {
                deleteReminder(
                    reminder.id
                );
            }
        );

        actionsCell.appendChild(
            deleteButton
        );


        // --------------------------------
        // Add columns to row
        // --------------------------------

        row.appendChild(
            messageCell
        );

        row.appendChild(
            recipientCell
        );

        row.appendChild(
            scheduleCell
        );

        row.appendChild(
            statusCell
        );

        row.appendChild(
            actionsCell
        );


        reminderTableBody.appendChild(
            row
        );

    });
}

function startReportEdit(reportId) {
    const report = reports.find(
        (item) => item.id === reportId
    );

    if (!report) {
        alert("Report not found.");
        return;
    }

    editingReportIdInput.value = report.id;
    reportNameInput.value = report.report_name;
    taskTitleInput.value = report.task_title;
    reportMessageInput.value = report.message;
    reportDetailsInput.value = report.details || "";

    saveReportButton.textContent = "Update Report";

    cancelReportEditButton.classList.remove(
        "hidden"
    );

    reportNameInput.focus();
}

function resetReportForm() {
    reportForm.reset();

    editingReportIdInput.value = "";

    saveReportButton.textContent =
        "Save Report";

    cancelReportEditButton.classList.add(
        "hidden"
    );
}

async function deleteReport(reportId) {
    const confirmed = confirm(
        "Are you sure you want to delete this report?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `/api/reports/${reportId}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        if (!result.success) {
            alert(
                result.message ||
                "Unable to delete report."
            );
            return;
        }

        await loadReports();

        alert("Report deleted successfully.");

    } catch (error) {
        console.error(
            "Delete report error:",
            error
        );

        alert("Unable to connect to the server.");
    }
}

async function toggleReminderStatus(reminderId) {
    const reminder = reminders.find(
        (item) => item.id === reminderId
    );

    if (!reminder) {
        alert("Reminder not found.");
        return;
    }

    const newStatus = !reminder.isActive;

    try {
        const response = await fetch(
            `/api/reminders/${reminderId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    is_active: newStatus
                })
            }
        );

        const result = await response.json();

        console.log("Status update response:", result);

        if (result.success) {
            await loadReminders();
        } else {
            alert(
                result.message ||
                "Unable to update reminder status."
            );
        }

    } catch (error) {
        console.error(
            "Update reminder status error:",
            error
        );

        alert("Unable to connect to the server.");
    }
}


async function deleteReminder(reminderId) {
    const confirmed = confirm(
        "Are you sure you want to delete this reminder?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `/api/reminders/${reminderId}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        console.log("Delete response:", result);

        if (result.success) {
            alert("Reminder deleted successfully.");

            await loadReminders();
        } else {
            alert(result.message || "Unable to delete reminder.");
        }

    } catch (error) {
        console.error("Delete reminder error:", error);

        alert("Unable to connect to the server.");
    }
}

async function handleReminderSubmit(event) {
    event.preventDefault();

    const selectedReportId = Number(
        reportSelect.value
    );

    if (!selectedReportId) {
        alert("Please select a report.");
        return;
    }

    const selectedReport = reports.find(
        (report) => report.id === selectedReportId
    );

    if (!selectedReport) {
        alert("Selected report was not found.");
        return;
    }

    const selectedRecipients =
        getSelectedRecipients();

    if (selectedRecipients.length === 0) {
        recipientError.classList.remove("hidden");
        return;
    }

    recipientError.classList.add("hidden");

    const scheduleTime =
        scheduleTimeInput.value;

    if (!scheduleTime) {
        alert("Schedule time is required.");
        return;
    }

    const reminderData = {
        report_id: selectedReport.id,

        // Save a snapshot of the report message
        message: selectedReport.message,

        recipients: selectedRecipients,

        repeat_type: repeatType.value,

        schedule_date:
            repeatType.value === "once"
                ? scheduleDate.value || null
                : null,

        schedule_time: scheduleTime,

        week_day:
            repeatType.value === "weekly"
                ? weekDay.value || null
                : null
    };

    console.log(
        "Reminder request:",
        reminderData
    );

    try {
        const response = await fetch(
            "/api/reminders",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    reminderData
                )
            }
        );

        const result = await response.json();

        console.log(
            "Create reminder response:",
            result
        );

        if (!result.success) {
            alert(
                result.message ||
                "Unable to save reminder."
            );

            return;
        }

        alert("Reminder saved successfully.");

        closeReminderModal();

        await loadReminders();

    } catch (error) {
        console.error(
            "Save reminder error:",
            error
        );

        alert(
            "Unable to connect to the server."
        );
    }
}

async function loadReminders() {
    try {
        const response = await fetch("/api/reminders");

        const result = await response.json();

        console.log("Loaded reminders:", result);

        if (!result.success) {
            alert(result.message || "Unable to load reminders.");
            return;
        }

        reminders = result.reminders.map((reminder) => {
            return {
                id: reminder.id,

                reportName:
                    reminder.report_name || "Unnamed Report",

                taskTitle:
                    reminder.task_title || "",

                message: reminder.message,
                recipients: reminder.recipients,
                repeatType: reminder.repeat_type,
                scheduleDate: reminder.schedule_date,
                scheduleTime: reminder.schedule_time,
                weekDay: reminder.week_day,
                isActive: reminder.is_active,
                completed: reminder.completed || false,
                status: reminder.status || "active",
            };
        });

        renderReminders();

    } catch (error) {
        console.error("Load reminders error:", error);
    }
}

openReminderFormButton.addEventListener(
    "click",
    openReminderModal
);


closeReminderFormButton.addEventListener(
    "click",
    closeReminderModal
);


cancelReminderButton.addEventListener(
    "click",
    closeReminderModal
);

repeatType.addEventListener(
    "change",
    updateScheduleFields
);

selectAllContactsButton.addEventListener(
    "click",
    () => {
        const visibleCheckboxes =
            contactList.querySelectorAll(
                'input[type="checkbox"]'
            );

        if (visibleCheckboxes.length === 0) {
            return;
        }

        const allVisibleSelected =
            Array.from(visibleCheckboxes).every(
                (checkbox) =>
                    selectedContactIds.has(
                        checkbox.value
                    )
            );

        visibleCheckboxes.forEach(
            (checkbox) => {
                checkbox.checked =
                    !allVisibleSelected;

                if (!allVisibleSelected) {
                    selectedContactIds.add(
                        checkbox.value
                    );
                } else {
                    selectedContactIds.delete(
                        checkbox.value
                    );
                }
            }
        );

        selectAllContactsButton.textContent =
            allVisibleSelected
                ? "Select all"
                : "Clear visible";
    }
);

selectAllGroupsButton.addEventListener("click", () => {
    toggleAllRecipients(
        groupList,
        selectAllGroupsButton
    );
});

reminderForm.addEventListener(
    "submit",
    handleReminderSubmit
);

addContactButton.addEventListener(
    "click",
    addSavedContact
);

reportForm.addEventListener(
    "submit",
    handleReportSubmit
);

reportSelect.addEventListener(
    "change",
    updateReportPreview
);

cancelReportEditButton.addEventListener(
    "click",
    resetReportForm
);

if (contactSearchInput) {
    contactSearchInput.addEventListener(
        "input",
        () => {
            loadContacts(contactSearchInput.value);
        }
    );
}

if (openReportsButton) {
    openReportsButton.addEventListener(
        "click",
        openReportsModal
    );
} else {
    console.error(
        "openReportsButton element not found"
    );
}

if (closeReportsButton) {
    closeReportsButton.addEventListener(
        "click",
        closeReportsModal
    );
} else {
    console.error(
        "closeReportsButton element not found"
    );
}

if (openReminderFormButton) {
    openReminderFormButton.addEventListener(
        "click",
        openReminderModal
    );
}

if (closeReminderFormButton) {
    closeReminderFormButton.addEventListener(
        "click",
        closeReminderModal
    );
}

if (cancelReminderButton) {
    cancelReminderButton.addEventListener(
        "click",
        closeReminderModal
    );
}

if (openReportsButton) {
    openReportsButton.addEventListener(
        "click",
        openReportsModal
    );
}

if (closeReportsButton) {
    closeReportsButton.addEventListener(
        "click",
        closeReportsModal
    );
}

if (addContactButton) {
    addContactButton.addEventListener(
        "click",
        addSavedContact
    );
}

if (reportForm) {
    reportForm.addEventListener(
        "submit",
        handleReportSubmit
    );
}

if (reminderForm) {
    reminderForm.addEventListener(
        "submit",
        handleReminderSubmit
    );
}

if (reportSearchInput) {

    reportSearchInput.addEventListener(
        "input",
        () => {

            renderReports(
                reportSearchInput.value
            );

        }
    );
}

if (reminderSearchInput) {

    console.log(
        "Reminder search input connected"
    );

    reminderSearchInput.addEventListener(
        "input",
        function () {
            renderReminders(
                reminderSearchInput.value
            );
        }
    );

} else {

    console.error(
        "reminderSearchInput not found"
    );
}

document
    .querySelectorAll(".modal-overlay")
    .forEach((overlay) => {

        overlay.addEventListener("click", () => {

            const modalId = overlay.dataset.closeModal;

            const modal = document.getElementById(
                modalId
            );

            if (modal) {
                modal.classList.add("hidden");
            }

        });

    });

document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {
        reminderModal.classList.add("hidden");
        reportsModal.classList.add("hidden");
    }

});

loadReports();
loadSavedContacts();
loadWhatsAppRecipients();
updateScheduleFields();
renderReminders();
loadReminders();