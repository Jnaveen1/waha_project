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

        alert("Contact saved successfully.");

    } catch (error) {
        console.error(
            "Save contact error:",
            error
        );

        alert("Unable to connect to the server.");
    }
}

function loadContacts() {
    contactList.innerHTML = "";

    if (contacts.length === 0) {
        contactList.innerHTML = `
            <p class="empty-message">
                No saved contacts found.
            </p>
        `;

        return;
    }

    contacts.forEach((contact) => {
        const item = document.createElement("label");

        item.className = "recipient-item";

        const checkbox = document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.value = contact.chat_id;
        checkbox.dataset.name = contact.name;
        checkbox.dataset.type = "contact";

        const details = document.createElement("span");

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
    const selectedCheckboxes = document.querySelectorAll(
        '.recipient-list input[type="checkbox"]'
    );

    selectedCheckboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });

    selectAllContactsButton.textContent = "Select all";
    selectAllGroupsButton.textContent = "Select all";
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
    const selectedCheckboxes = document.querySelectorAll(
        '.recipient-list input[type="checkbox"]:checked'
    );

    return Array.from(selectedCheckboxes).map((checkbox) => {
        return {
            recipient_name: checkbox.dataset.name,
            chat_id: checkbox.value,
            recipient_type: checkbox.dataset.type
        };
    });
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


function createStatusBadge(isActive) {
    const badge = document.createElement("span");

    badge.textContent = isActive ? "Active" : "Inactive";

    badge.style.padding = "5px 10px";
    badge.style.borderRadius = "12px";
    badge.style.fontSize = "13px";

    if (isActive) {
        badge.style.background = "#d1e7dd";
        badge.style.color = "#0f5132";
    } else {
        badge.style.background = "#f8d7da";
        badge.style.color = "#842029";
    }

    return badge;
}


function renderReminders() {
    reminderTableBody.innerHTML = "";

    reminderCount.textContent =
        `${reminders.length} reminder${reminders.length === 1 ? "" : "s"}`;

    if (reminders.length === 0) {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td colspan="5" class="empty-message">
                No reminders created yet.
            </td>
        `;

        reminderTableBody.appendChild(row);

        return;
    }

    reminders.forEach((reminder) => {
        const row = document.createElement("tr");

        const messageCell = document.createElement("td");
        messageCell.textContent = reminder.message;

        const recipientCell = document.createElement("td");
        recipientCell.textContent = reminder.recipients
            .map((recipient) => recipient.recipient_name)
            .join(", ");

        const scheduleCell = document.createElement("td");
        scheduleCell.textContent = formatSchedule(reminder);

        const statusCell = document.createElement("td");
        statusCell.appendChild(
            createStatusBadge(reminder.isActive)
        );

        const actionsCell = document.createElement("td");

        const toggleButton = document.createElement("button");

        toggleButton.type = "button";
        toggleButton.className = "text-button";
        toggleButton.textContent = reminder.isActive
            ? "Disable"
            : "Enable";

        toggleButton.addEventListener("click", () => {
            toggleReminderStatus(reminder.id);
        });

        const deleteButton = document.createElement("button");

        deleteButton.type = "button";
        deleteButton.className = "text-button";
        deleteButton.textContent = "Delete";
        deleteButton.style.marginLeft = "12px";
        deleteButton.style.color = "#dc3545";

        deleteButton.addEventListener("click", () => {
            deleteReminder(reminder.id);
        });

        actionsCell.appendChild(toggleButton);
        actionsCell.appendChild(deleteButton);

        row.appendChild(messageCell);
        row.appendChild(recipientCell);
        row.appendChild(scheduleCell);
        row.appendChild(statusCell);
        row.appendChild(actionsCell);

        reminderTableBody.appendChild(row);
    });
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

    const selectedRecipients = getSelectedRecipients();

    if (selectedRecipients.length === 0) {
        recipientError.classList.remove("hidden");
        return;
    }

    recipientError.classList.add("hidden");

    const newReminder = {
        message: document
            .getElementById("reminderMessage")
            .value
            .trim(),

        recipients: selectedRecipients,

        repeat_type: repeatType.value,

        schedule_date: scheduleDate.value || null,

        schedule_time: document
            .getElementById("scheduleTime")
            .value,

        week_day: weekDay.value || null
    };

    if (!newReminder.message) {
        alert("Reminder message is required.");
        return;
    }

    if (!newReminder.schedule_time) {
        alert("Schedule time is required.");
        return;
    }

    try {
        const response = await fetch("/api/reminders", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(newReminder)
        });

        const result = await response.json();

        console.log("Backend response:", result);

        if (result.success) {
            alert("Reminder saved successfully.");

            closeReminderModal();

             await loadReminders();

            // We will load reminders from MySQL in the next step.
        } else {
            alert(result.message || "Unable to save reminder.");
        }

    } catch (error) {
        console.error("Save reminder error:", error);

        alert("Unable to connect to the server.");
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
                message: reminder.message,
                recipients: reminder.recipients,
                repeatType: reminder.repeat_type,
                scheduleDate: reminder.schedule_date,
                scheduleTime: reminder.schedule_time,
                weekDay: reminder.week_day,
                isActive: reminder.is_active
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


selectAllContactsButton.addEventListener("click", () => {
    toggleAllRecipients(
        contactList,
        selectAllContactsButton
    );
});


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

document
    .querySelector(".modal-overlay")
    .addEventListener("click", closeReminderModal);



loadSavedContacts();
loadWhatsAppRecipients();
updateScheduleFields();
renderReminders();
loadReminders();