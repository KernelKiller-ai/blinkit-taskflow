const BASE_URL = "http://127.0.0.1:8000";
const TASKS_URL = `${BASE_URL}/api/tasks`;
const PROJECTS_URL = `${BASE_URL}/api/projects`;
const USERS_URL = `${BASE_URL}/api/users`;

const state = {
  tasks: [],
  projects: [],
  currentUserId: null,
};

// DOM Elements - Modals
const taskModal = document.getElementById("task-modal");
const openTaskModalBtn = document.getElementById("open-task-modal");
const closeTaskModalBtn = document.getElementById("close-task-modal");

const projectModal = document.getElementById("project-modal");
const openProjectModalBtn = document.getElementById("open-project-modal");
const closeProjectModalBtn = document.getElementById("close-project-modal");

// DOM Elements - Forms & Inputs
const taskForm = document.getElementById("task-form");
const taskTitleInput = document.getElementById("task-title");
const titleError = document.getElementById("title-error");
const taskDueDateInput = document.getElementById("task-due-date");
const taskPrioritySelect = document.getElementById("task-priority");
const taskProjectSelect = document.getElementById("task-project");

const projectForm = document.getElementById("project-form");
const projectNameInput = document.getElementById("project-name");

const quickAddForm = document.getElementById("quick-add-form");
const quickDescriptionInput = document.getElementById("quick-description");

const searchForm = document.getElementById("search-form");
const searchTitleInput = document.getElementById("search-title");
const searchAlgoSelect = document.getElementById("search-algo");
const globalSearchInput = document.getElementById("global-search-input");
const sortButton = document.getElementById("sort-button");
const refreshButton = document.getElementById("refresh-button");

// DOM Elements - Containers & Stats
const taskList = document.getElementById("task-list");
const statsContainer = document.getElementById("stats-container");
const statTotalEl = document.getElementById("stat-total");
const statCompletedEl = document.getElementById("stat-completed");
const statPendingEl = document.getElementById("stat-pending");
const statProjectsEl = document.getElementById("stat-projects");

// --- MODAL CONTROLS ---
function toggleModal(modal, show) {
  if (!modal) return;
  modal.classList.toggle("active", show);
}

if (openTaskModalBtn)
  openTaskModalBtn.addEventListener("click", () =>
    toggleModal(taskModal, true),
  );
if (closeTaskModalBtn)
  closeTaskModalBtn.addEventListener("click", () =>
    toggleModal(taskModal, false),
  );

if (openProjectModalBtn)
  openProjectModalBtn.addEventListener("click", () =>
    toggleModal(projectModal, true),
  );
if (closeProjectModalBtn)
  closeProjectModalBtn.addEventListener("click", () =>
    toggleModal(projectModal, false),
  );

window.addEventListener("click", (e) => {
  if (e.target === taskModal) toggleModal(taskModal, false);
  if (e.target === projectModal) toggleModal(projectModal, false);
});

// --- LOCAL STORAGE HELPERS ---
function readCachedTasks() {
  try {
    const cached = localStorage.getItem("task_cache");
    if (!cached) return [];
    const parsed = JSON.parse(cached);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.warn("Could not read task cache", error);
    return [];
  }
}

function saveCachedTasks(tasks) {
  localStorage.setItem("task_cache", JSON.stringify(tasks));
}

// --- ERROR HELPERS ---
function showTitleError(message) {
  if (titleError) titleError.textContent = message;
  if (taskTitleInput)
    taskTitleInput.classList.toggle("invalid", Boolean(message));
}

function clearTitleError() {
  showTitleError("");
}

// --- STATS OVERVIEW UPDATER ---
function updateOverviewStats() {
  const total = state.tasks.length;
  const completed = state.tasks.filter((t) => t.completed).length;
  const pending = total - completed;
  const projectCount = state.projects.length;

  if (statTotalEl) statTotalEl.textContent = total;
  if (statCompletedEl) statCompletedEl.textContent = completed;
  if (statPendingEl) statPendingEl.textContent = pending;
  if (statProjectsEl) statProjectsEl.textContent = projectCount;
}

// --- RENDER FUNCTIONS (Safe DOM with createElement) ---
function renderTasks(tasks) {
  state.tasks = tasks;
  saveCachedTasks(tasks);
  updateOverviewStats();

  if (!taskList) return;
  taskList.innerHTML = "";

  if (!tasks || !tasks.length) {
    const emptyMessage = document.createElement("div");
    emptyMessage.className = "empty-state";
    emptyMessage.style.textAlign = "center";
    emptyMessage.style.padding = "2.5rem 1rem";
    emptyMessage.style.color = "var(--text-muted)";
    emptyMessage.innerHTML = `
      <i class="fa-solid fa-clipboard-list" style="font-size: 32px; margin-bottom: 8px; display: block; opacity: 0.5;"></i>
      <p>No active tasks found.</p>
      <small>Use AI Quick-Add or create a new task above.</small>
    `;
    taskList.appendChild(emptyMessage);
    return;
  }

  const fragment = document.createDocumentFragment();
  tasks.forEach((task) => {
    const card = document.createElement("article");
    card.className = `task-item ${task.completed ? "completed" : ""}`;

    const main = document.createElement("div");
    main.className = "task-item-main";

    const title = document.createElement("h3");
    title.className = "task-title";
    title.textContent = task.title || "Untitled task";

    let projName = "No project Pod";
    if (task.project_id && state.projects.length) {
      const found = state.projects.find((p) => p.id === task.project_id);
      if (found) projName = found.name;
    }

    const meta = document.createElement("p");
    meta.className = "task-meta";
    const priorityLabel = (task.priority || "medium").toString().toLowerCase();
    const dueLabel = task.due_date
      ? `📅 Due: ${task.due_date}`
      : "📅 No due date";
    meta.textContent = `${dueLabel} • 📁 ${projName}`;

    const status = document.createElement("span");
    status.className = `priority-pill priority-${priorityLabel}`;
    status.textContent = priorityLabel;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-checkbox";
    checkbox.checked = Boolean(task.completed);
    checkbox.style.marginRight = "10px";
    checkbox.style.cursor = "pointer";
    checkbox.addEventListener("change", () =>
      handleToggleCompleted(task, checkbox.checked),
    );

    const titleContainer = document.createElement("div");
    titleContainer.style.display = "flex";
    titleContainer.style.alignItems = "center";
    titleContainer.appendChild(checkbox);
    titleContainer.appendChild(title);

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "✏️ Edit";
    editButton.addEventListener("click", () => handleEdit(task));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-btn";
    deleteButton.textContent = "🗑️ Delete";
    deleteButton.addEventListener("click", () => handleDelete(task.id));

    main.appendChild(status);
    main.appendChild(titleContainer);
    main.appendChild(meta);
    actions.appendChild(editButton);
    actions.appendChild(deleteButton);
    card.appendChild(main);
    card.appendChild(actions);
    fragment.appendChild(card);
  });

  taskList.appendChild(fragment);
}

function renderStats(stats) {
  if (!statsContainer) return;
  statsContainer.innerHTML = "";
  if (!stats || !stats.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.style.color = "var(--text-muted)";
    empty.style.fontSize = "0.85rem";
    empty.textContent = "No project statistics aggregated yet.";
    statsContainer.appendChild(empty);
    return;
  }

  const fragment = document.createDocumentFragment();
  stats.forEach((stat) => {
    const row = document.createElement("div");
    row.className = "stat-item";

    const name = document.createElement("span");
    name.textContent = stat.project_name;
    name.style.fontWeight = "600";

    const count = document.createElement("strong");
    count.textContent = `${stat.task_count} tasks`;
    count.style.background = "#f1f5f9";
    count.style.padding = "2px 8px";
    count.style.borderRadius = "6px";

    row.appendChild(name);
    row.appendChild(count);
    fragment.appendChild(row);
  });
  statsContainer.appendChild(fragment);
}

function populateProjectOptions() {
  if (!taskProjectSelect) return;
  taskProjectSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select project pod";
  taskProjectSelect.appendChild(placeholder);

  state.projects.forEach((project) => {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.name;
    taskProjectSelect.appendChild(option);
  });
}

// --- USER INITIALIZATION ---
async function ensureDefaultUser() {
  if (state.currentUserId) return state.currentUserId;
  try {
    const getRes = await fetch(USERS_URL);
    if (getRes.ok) {
      const users = await getRes.json();
      if (users && users.length > 0) {
        state.currentUserId = users[0].id;
        return users[0].id;
      }
    }

    const response = await fetch(USERS_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Anurag Kumar",
        email: "anurag@example.com",
      }),
    });

    if (response.ok) {
      const user = await response.json();
      state.currentUserId = user.id;
      return user.id;
    }
  } catch (error) {
    console.warn("User fetch fallback active", error);
  }
  state.currentUserId = 1;
  return 1;
}

// --- API FETCHERS ---
async function fetchProjects() {
  try {
    const response = await fetch(PROJECTS_URL);
    if (!response.ok) throw new Error("Unable to fetch projects");
    state.projects = await response.json();
    populateProjectOptions();
    updateOverviewStats();
  } catch (error) {
    console.error("Could not fetch projects", error);
  }
}

async function fetchTasks() {
  const cachedTasks = readCachedTasks();
  if (cachedTasks.length) renderTasks(cachedTasks);

  try {
    const response = await fetch(TASKS_URL);
    if (!response.ok) throw new Error("Unable to fetch tasks");
    const tasks = await response.json();
    renderTasks(tasks);
  } catch (error) {
    console.error("Could not fetch tasks", error);
  }
}

async function fetchStats() {
  try {
    const response = await fetch(`${PROJECTS_URL}/stats`);
    if (!response.ok) throw new Error("Unable to fetch stats");
    renderStats(await response.json());
  } catch (error) {
    console.error("Could not fetch stats", error);
  }
}

async function createTask(payload) {
  const response = await fetch(TASKS_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Unable to create task");
  await Promise.all([fetchTasks(), fetchStats()]);
}

async function quickAddTask(description) {
  const userId = await ensureDefaultUser();
  const selectedProj = taskProjectSelect ? taskProjectSelect.value : null;
  const projectId = selectedProj ? parseInt(selectedProj, 10) : null;

  const response = await fetch(`${TASKS_URL}/quick-add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      description,
      user_id: userId,
      project_id: projectId,
    }),
  });
  if (!response.ok) throw new Error("Unable to quick-add task");
  await Promise.all([fetchTasks(), fetchStats()]);
}

async function handleDelete(taskId) {
  if (!window.confirm("Are you sure you want to delete this task?")) return;
  const response = await fetch(`${TASKS_URL}/${taskId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Unable to delete task");
  await Promise.all([fetchTasks(), fetchStats()]);
}

async function handleToggleCompleted(task, completedStatus) {
  const response = await fetch(`${TASKS_URL}/${task.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: task.title,
      priority: task.priority,
      completed: completedStatus,
      user_id: task.user_id,
      project_id: task.project_id,
    }),
  });
  if (!response.ok) throw new Error("Unable to update task status");
  await Promise.all([fetchTasks(), fetchStats()]);
}

async function handleEdit(task) {
  const newTitle = window.prompt("Edit task title", task.title || "");
  if (newTitle === null) return;
  const trimmed = newTitle.trim();
  if (!trimmed) {
    window.alert("Title cannot be empty.");
    return;
  }
  const response = await fetch(`${TASKS_URL}/${task.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: trimmed,
      priority: task.priority,
      completed: task.completed,
      user_id: task.user_id,
      project_id: task.project_id,
    }),
  });
  if (!response.ok) throw new Error("Unable to update task");
  await Promise.all([fetchTasks(), fetchStats()]);
}

async function searchTasks(title, algo) {
  const response = await fetch(
    `${TASKS_URL}/search?title=${encodeURIComponent(title)}&algo=${encodeURIComponent(algo)}`,
  );
  if (!response.ok) throw new Error("Task not found");
  renderTasks(await response.json());
}

async function sortTasks() {
  const response = await fetch(`${TASKS_URL}?sort=priority`);
  if (!response.ok) throw new Error("Unable to sort tasks");
  renderTasks(await response.json());
}

// --- EVENT LISTENERS ---
if (taskForm) {
  taskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = taskTitleInput ? taskTitleInput.value.trim() : "";
    if (!title) {
      showTitleError("Title is required.");
      if (taskTitleInput) taskTitleInput.focus();
      return;
    }
    clearTitleError();

    const userId = await ensureDefaultUser();
    const selectedProj = taskProjectSelect ? taskProjectSelect.value : null;
    const projectId = selectedProj ? parseInt(selectedProj, 10) : null;

    try {
      await createTask({
        title,
        description: "",
        priority: taskPrioritySelect ? taskPrioritySelect.value : "medium",
        due_date:
          taskDueDateInput && taskDueDateInput.value
            ? taskDueDateInput.value
            : null,
        user_id: userId,
        project_id: projectId,
      });
      taskForm.reset();
      clearTitleError();
      toggleModal(taskModal, false);
    } catch (err) {
      showTitleError("Failed to save task.");
    }
  });
}

if (projectForm) {
  projectForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = projectNameInput ? projectNameInput.value.trim() : "";
    if (!name) {
      window.alert("Project name cannot be empty.");
      return;
    }
    const userId = await ensureDefaultUser();

    try {
      const res = await fetch(PROJECTS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, owner_id: userId }),
      });
      if (!res.ok) throw new Error();
      if (projectNameInput) projectNameInput.value = "";
      await fetchProjects();
      await fetchStats();
      toggleModal(projectModal, false);
    } catch (err) {
      window.alert("Failed to create project pod.");
    }
  });
}

if (quickAddForm) {
  quickAddForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const desc = quickDescriptionInput
      ? quickDescriptionInput.value.trim()
      : "";
    if (!desc) return;
    try {
      await quickAddTask(desc);
      quickAddForm.reset();
    } catch (err) {
      console.error("AI Quick-add failed", err);
    }
  });
}

if (searchForm) {
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = searchTitleInput ? searchTitleInput.value.trim() : "";
    const algo = searchAlgoSelect ? searchAlgoSelect.value : "binary";
    searchTasks(title, algo).catch(() =>
      window.alert("Task not found via algorithm search."),
    );
  });
}

if (globalSearchInput) {
  globalSearchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    if (searchTitleInput) searchTitleInput.value = val;
    if (val === "") {
      fetchTasks();
    } else {
      searchTasks(val, "linear").catch(() => {});
    }
  });
}

if (sortButton) sortButton.addEventListener("click", () => sortTasks());
if (refreshButton)
  refreshButton.addEventListener("click", () => {
    fetchTasks();
    fetchStats();
  });

if (taskTitleInput) {
  taskTitleInput.addEventListener("input", () => {
    if (taskTitleInput.value.trim()) clearTitleError();
  });
}

// --- INITIALIZE MOUNT ---
window.addEventListener("DOMContentLoaded", async () => {
  const cached = readCachedTasks();
  if (cached.length) renderTasks(cached);
  try {
    await fetchProjects();
    await ensureDefaultUser();
    await Promise.all([fetchTasks(), fetchStats()]);
  } catch (err) {
    console.error("Initialization sync error", err);
  }
});
