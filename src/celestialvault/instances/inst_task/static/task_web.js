let nodeStatuses = {};
let errors = [];
let refreshRate = 5000;
let refreshIntervalId = null;

const statusIndicator = document.getElementById("status-indicator");
const refreshSelect = document.getElementById("refresh-interval");
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");
const dashboardGrid = document.getElementById("dashboard-grid");
const structureView = document.getElementById("structure-view");
const nodeFilter = document.getElementById("node-filter");
const errorsTableBody = document.querySelector("#errors-table tbody");
const totalProcessed = document.getElementById("total-processed");
const totalPending = document.getElementById("total-pending");
const totalErrors = document.getElementById("total-errors");
const totalNodes = document.getElementById("total-nodes");
const shutdownBtn = document.getElementById("shutdown-btn");

document.addEventListener("DOMContentLoaded", () => {
  refreshSelect.addEventListener("change", () => {
    refreshRate = parseInt(refreshSelect.value);
    clearInterval(refreshIntervalId);
    refreshIntervalId = setInterval(refreshAll, refreshRate);
  });

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.getAttribute("data-tab");
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(tab).classList.add("active");
    });
  });

  shutdownBtn.addEventListener("click", async () => {
    if (confirm("确认要关闭 Web 服务吗？")) {
      const res = await fetch("/shutdown", { method: "POST" });
      const text = await res.text();
      alert(text);
    }
  });

  refreshAll();
  refreshIntervalId = setInterval(refreshAll, refreshRate);
});

async function refreshAll() {
  await Promise.all([loadStatuses(), loadStructure(), loadErrors()]);
  renderDashboard();
  updateSummary();
  renderErrors();
  populateNodeFilter();
}

async function loadStatuses() {
  try {
    const res = await fetch("/api/status");
    nodeStatuses = await res.json();
  } catch (e) {
    console.error("状态加载失败", e);
  }
}

async function loadStructure() {
  try {
    const res = await fetch("/api/structure");
    const structure = await res.json();
    structureView.textContent = structure.join("\n");
  } catch (e) {
    console.error("结构加载失败", e);
  }
}

async function loadErrors() {
  try {
    const res = await fetch("/api/errors");
    errors = await res.json();
  } catch (e) {
    console.error("错误日志加载失败", e);
  }
}

function renderDashboard() {
  dashboardGrid.innerHTML = "";
  for (const [node, data] of Object.entries(nodeStatuses)) {
    const progress =
      data.tasks_processed + data.tasks_pending === 0
        ? 0
        : Math.round(
            (data.tasks_processed /
              (data.tasks_processed + data.tasks_pending)) *
              100
          );

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
          <div class="card-header">
            <h3 class="card-title">${node}</h3>
            <span class="badge ${
              data.active ? "badge-success" : "badge-inactive"
            }">
              ${data.active ? "运行中" : "已停止"}
            </span>
          </div>
          <div class="stats-grid">
            <div><div class="stat-label">已处理</div><div class="stat-value">${
              data.tasks_processed
            }</div></div>
            <div><div class="stat-label">等待中</div><div class="stat-value">${
              data.tasks_pending
            }</div></div>
            <div><div class="stat-label">错误</div><div class="stat-value text-red">${
              data.tasks_error
            }</div></div>
            <div><div class="stat-label">模式</div><div class="stat-value">${
              data.execution_mode
            }</div></div>
          </div>
          <div class="text-sm text-gray">开始时间: ${new Date(
            data.start_time
          ).toLocaleString()}</div>
          <div class="progress-container">
            <div class="progress-header">
              <span>任务完成率</span>
              <span>${progress}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-value" style="width: ${progress}%"></div>
            </div>
          </div>
        `;
    dashboardGrid.appendChild(card);
  }
}

function updateSummary() {
  let processed = 0,
    pending = 0,
    error = 0,
    active = 0;
  Object.values(nodeStatuses).forEach((s) => {
    processed += s.tasks_processed;
    pending += s.tasks_pending;
    error += s.tasks_error;
    if (s.active) active++;
  });
  totalProcessed.textContent = processed;
  totalPending.textContent = pending;
  totalErrors.textContent = error;
  totalNodes.textContent = active;
}

function renderErrors() {
  const filter = nodeFilter.value;
  const filtered = filter ? errors.filter((e) => e.node === filter) : errors;

  errorsTableBody.innerHTML = "";
  if (!filtered.length) {
    errorsTableBody.innerHTML = `<tr><td colspan="4" class="no-errors">没有错误记录</td></tr>`;
    return;
  }

  for (const e of filtered) {
    const row = document.createElement("tr");
    row.innerHTML = `
          <td class="error-message">${e.error}</td>
          <td>${e.node}</td>
          <td>${e.task_id}</td>
          <td>${new Date(e.timestamp).toLocaleString()}</td>
        `;
    errorsTableBody.appendChild(row);
  }
}

function populateNodeFilter() {
  const nodes = Object.keys(nodeStatuses);
  nodeFilter.innerHTML = `<option value="">全部节点</option>`;
  for (const node of nodes) {
    const option = document.createElement("option");
    option.value = node;
    option.textContent = node;
    nodeFilter.appendChild(option);
  }
}
