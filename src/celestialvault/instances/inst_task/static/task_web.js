let nodeStatuses = {};
let errors = [];
let refreshRate = 5000;
let refreshIntervalId = null;

const themeToggleBtn = document.getElementById("theme-toggle");
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

// 初始化折叠节点记录
let collapsedNodeIds = new Set(
  JSON.parse(localStorage.getItem("collapsedNodes") || "[]")
);

document.addEventListener("DOMContentLoaded", async () => {
  refreshSelect.addEventListener("change", () => {
    refreshRate = parseInt(refreshSelect.value);
    clearInterval(refreshIntervalId);
    refreshIntervalId = setInterval(refreshAll, refreshRate);
    pushRefreshRate(); // ✅ 立即同步到后端
  });

  themeToggleBtn.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark-theme");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    themeToggleBtn.textContent = isDark ? "🌞 白天模式" : "🌙 夜间模式";
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

  nodeFilter.addEventListener("change", () => {
    renderErrors();
  });

  // 初始化时应用之前选择的主题
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-theme");
    themeToggleBtn.textContent = "🌞 白天模式";
  } else {
    themeToggleBtn.textContent = "🌙 夜间模式";
  }

  // 启动轮询
  refreshAll();
  pushRefreshRate(); // ✅ 初次加载也推送一次
  refreshIntervalId = setInterval(refreshAll, refreshRate);
});

async function pushRefreshRate() {
  try {
    await fetch("/api/push_interval", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ interval: refreshRate }),
    });
  } catch (e) {
    console.warn("刷新频率推送失败", e);
  }
}

async function refreshAll() {
  await Promise.all([loadStatuses(), loadStructure(), loadErrors()]);
  renderDashboard();
  updateSummary();
  renderErrors();
  populateNodeFilter();
}

async function loadStatuses() {
  try {
    const res = await fetch("/api/get_status");
    nodeStatuses = await res.json();
  } catch (e) {
    console.error("状态加载失败", e);
  }
}

async function loadStructure() {
  try {
    const res = await fetch("/api/get_structure");
    const data = await res.json(); // 结构是结构化 JSON

    // 判断是否为空对象或空数组
    if (Object.keys(data).length === 0) {
      return;
    }

    renderTree(data);
  } catch (e) {
    console.error("结构加载失败", e);
  }
}

function renderTree(data) {
  const treeContainer = document.getElementById("task-tree");
  treeContainer.innerHTML = "";

  function buildTreeHTML(node, path = "") {
    const nodeId = path ? `${path}/${node.stage_name}` : node.stage_name;
    let html = "<li>";

    // 节点展示内容
    html += `<div class="tree-node collapsible" data-id="${nodeId}" onclick="toggleNode(this)">`;

    if (node.next_stages && node.next_stages.length > 0) {
      html += `<span class="collapse-icon">${
        collapsedNodeIds.has(nodeId) ? "+" : "-"
      }</span>`;
    }

    html += `<span class="stage-name">${node.stage_name}</span>`;
    html += `<span class="stage-mode">(stage_mode: ${node.stage_mode})</span>`;
    html += `<span class="stage-func">func: ${node.func_name}</span>`;

    if (node.visited) {
      html += `<span class="visited-mark">already visited</span>`;
    }

    html += "</div>";

    // 子节点递归渲染
    if (node.next_stages && node.next_stages.length > 0) {
      const isCollapsed = collapsedNodeIds.has(nodeId);
      html += `<ul ${isCollapsed ? 'class="hidden"' : ""}>`;
      node.next_stages.forEach((childNode) => {
        html += buildTreeHTML(childNode, nodeId);
      });
      html += "</ul>";
    }

    html += "</li>";
    return html;
  }

  const rootHTML = `<ul>${buildTreeHTML(data)}</ul>`;
  treeContainer.innerHTML = rootHTML;
}

// 节点折叠/展开，并保存到 localStorage
function toggleNode(element) {
  const childList = element.nextElementSibling;
  const nodeId = element.dataset.id;
  if (!nodeId || !childList || childList.tagName !== "UL") return;

  const isNowHidden = childList.classList.toggle("hidden");
  const icon = element.querySelector(".collapse-icon");
  if (icon) {
    icon.textContent = isNowHidden ? "+" : "-";
  }

  // 更新本地存储
  if (isNowHidden) {
    collapsedNodeIds.add(nodeId);
  } else {
    collapsedNodeIds.delete(nodeId);
  }
  localStorage.setItem("collapsedNodes", JSON.stringify([...collapsedNodeIds]));
}

// 切换主题
function toggleTheme() {
  document.body.classList.toggle("dark-theme");
}

async function loadErrors() {
  try {
    const res = await fetch("/api/get_errors");
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
        : Math.floor(
            ((data.tasks_processed + data.tasks_error) /
              (data.tasks_processed + data.tasks_error + data.tasks_pending)) *
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
              ${data.active ? "运行中" : "未运行"}
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
          <div class="text-sm text-gray">开始时间: ${data.start_time}</div>
          <div class="progress-container">
            <div class="progress-header">
              <span>任务完成率</span>
              <span class="time-estimate">
                <span class="elapsed">${data.elapsed_time}</span>
                &lt; 
                <span class="remaining">${data.remaining_time}</span>, 
                <span class="task-avg-time">${data.task_avg_time}</span>, 
                <span>${progress}%</span>
              </span>
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

  // 按时间戳降序排序（最新的错误排在最前面）
  const sortedByTime = [...filtered].sort((a, b) => b.timestamp - a.timestamp);

  for (const e of sortedByTime) {
    const row = document.createElement("tr");
    row.innerHTML = `
          <td class="error-message">${e.error}</td>
          <td>${e.node}</td>
          <td>${e.task_id}</td>
          <td>${formatTimestamp(e.timestamp)}</td>
        `;
    errorsTableBody.appendChild(row);
  }
}

function formatTimestamp(timestamp) {
  return new Date(timestamp * 1000).toLocaleString();
}

function populateNodeFilter() {
  const nodes = Object.keys(nodeStatuses);
  const previousValue = nodeFilter.value;  // 记住当前选中值

  // 重新填充选项
  nodeFilter.innerHTML = `<option value="">全部节点</option>`;
  for (const node of nodes) {
    const option = document.createElement("option");
    option.value = node;
    option.textContent = node;
    nodeFilter.appendChild(option);
  }

  // 尝试恢复之前的选中项
  if (nodes.includes(previousValue)) {
    nodeFilter.value = previousValue;
  } else {
    nodeFilter.value = "";  // 默认选“全部节点”
  }
}

