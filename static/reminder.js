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


const contacts = [
    {
        name: "Farm Manager",
        chatId: "919876543210@c.us"
    },
    {
        name: "Supervisor",
        chatId: "919123456789@c.us"
    },
    {
        name: "Account Manager",
        chatId: "919999999999@c.us"
    }
];


const groups = [
    {
        name: "Farm Group",
        chatId: "120363423099150354@g.us"
    },
    {
        name: "Management Group",
        chatId: "120363345095589925@g.us"
    },
    {
        name: "AI Intern Group",
        chatId: "120363422507401551@g.us"
    }
];


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


function createRecipientItem(recipient, type) {
    const item = document.createElement("label");

    item.className = "recipient-item";

    const checkbox = document.createElement("input");

    checkbox.type = "checkbox";
    checkbox.value = recipient.chatId;
    checkbox.dataset.name = recipient.name;
    checkbox.dataset.type = type;

    const recipientDetails = document.createElement("span");

    recipientDetails.textContent =
        `${recipient.name} (${recipient.chatId})`;

    item.appendChild(checkbox);
    item.appendChild(recipientDetails);

    return item;
}


function loadContacts() {
    contactList.innerHTML = "";

    contacts.forEach((contact) => {
        const item = createRecipientItem(contact, "contact");

        contactList.appendChild(item);
    });
}


function loadGroups() {
    groupList.innerHTML = "";

    groups.forEach((group) => {
        const item = createRecipientItem(group, "group");

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
            name: checkbox.dataset.name,
            chatId: checkbox.value,
            type: checkbox.dataset.type
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
            .map((recipient) => recipient.name)
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


function toggleReminderStatus(reminderId) {
    reminders = reminders.map((reminder) => {
        if (reminder.id === reminderId) {
            return {
                ...reminder,
                isActive: !reminder.isActive
            };
        }

        return reminder;
    });

    renderReminders();
}


function deleteReminder(reminderId) {
    const confirmed = window.confirm(
        "Are you sure you want to delete this reminder?"
    );

    if (!confirmed) {
        return;
    }

    reminders = reminders.filter(
        (reminder) => reminder.id !== reminderId
    );

    renderReminders();
}


function handleReminderSubmit(event) {
    event.preventDefault();

    const selectedRecipients = getSelectedRecipients();

    if (selectedRecipients.length === 0) {
        recipientError.classList.remove("hidden");

        return;
    }

    recipientError.classList.add("hidden");

    const newReminder = {
        id: Date.now(),

        message: document.getElementById(
            "reminderMessage"
        ).value.trim(),

        recipients: selectedRecipients,

        repeatType: repeatType.value,

        scheduleDate: scheduleDate.value,

        scheduleTime: document.getElementById(
            "scheduleTime"
        ).value,

        weekDay: weekDay.value,

        isActive: true
    };

    reminders.push(newReminder);

    console.log("Reminder created:", newReminder);

    renderReminders();

    closeReminderModal();
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


document
    .querySelector(".modal-overlay")
    .addEventListener("click", closeReminderModal);


loadContacts();
loadGroups();
updateScheduleFields();
renderReminders();