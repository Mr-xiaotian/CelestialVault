let nodeStatuses = {};
let errors = [];
let refreshRate = 5000;
let refreshIntervalId = null;
let progressChart = null;
let draggingNodeName = null;
let hiddenNodes = new Set(
  JSON.parse(localStorage.getItem("hiddenNodes") || "[]")
);

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

  initSortableDashboard(); // 初始化拖拽
  refreshAll(); // 启动轮询
  pushRefreshRate(); // ✅ 初次加载也推送一次
  initChart(); // 初始化折线图
  refreshIntervalId = setInterval(refreshAll, refreshRate);
});

function initSortableDashboard() {
  if (isMobile()) {
    console.log("移动端，禁用拖动功能");
    return;
  }

  const el = document.getElementById("dashboard-grid");
  new Sortable(el, {
    animation: 300,
    easing: "cubic-bezier(0.25, 1, 0.5, 1)",
    ghostClass: "sortable-ghost",
    chosenClass: "sortable-chosen",
    onStart: function (evt) {
      const title = evt.item.querySelector(".card-title").textContent;
      draggingNodeName = title;
    },
    onEnd: function (evt) {
      saveDashboardOrder();
      draggingNodeName = null;
    },
  });
}

function saveDashboardOrder() {
  const order = Array.from(
    document.querySelectorAll("#dashboard-grid .card-title")
  ).map((el) => el.textContent);
  localStorage.setItem("dashboardOrder", JSON.stringify(order));
}

function getDashboardOrder() {
  return JSON.parse(localStorage.getItem("dashboardOrder") || "[]");
}

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

  // 新增: 更新任务注入页面的节点列表
  if (typeof renderNodeList === "function") {
    renderNodeList();
  }

  // 在这里调用折线图更新
  const progressData = extractProgressData(nodeStatuses);
  updateChartData(progressData);
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
      html += `<span class="visited-mark">visited</span>`;
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

  const rootHTML = `${buildTreeHTML(data)}`;
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

  // 获取用户排序顺序
  const order = getDashboardOrder();
  const orderedEntries = Object.entries(nodeStatuses).sort((a, b) => {
    const indexA = order.indexOf(a[0]);
    const indexB = order.indexOf(b[0]);
    if (indexA === -1 && indexB === -1) return 0;
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  for (const [node, data] of orderedEntries) {
    if (node === draggingNodeName) continue; // 正在拖动时，不渲染它

    // ✅ 计算进度
    const progress =
      data.tasks_processed + data.tasks_pending === 0
        ? 0
        : Math.floor(
            ((data.tasks_processed + data.tasks_failed) /
              (data.tasks_processed + data.tasks_failed + data.tasks_pending)) *
              100
          );

    // ✅ 根据 status 决定 badge 样式和文本
    let badgeClass = "badge-inactive";
    let badgeText = "未运行";
    if (data.status === 1) {
      badgeClass = "badge-running";
      badgeText = "运行中";
    } else if (data.status === 2) {
      badgeClass = "badge-completed";
      badgeText = "已停止";
    }

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
          <div class="card-header">
            <h3 class="card-title">${node}</h3>
            <span class="badge ${badgeClass}">${badgeText}</span>
          </div>
          <div class="stats-grid">
            <div><div class="stat-label">已处理</div><div class="stat-value">${formatWithDelta(
              data.tasks_processed,
              data.add_tasks_processed
            )}</div></div>
            <div><div class="stat-label">等待中</div><div class="stat-value">${formatWithDelta(
              data.tasks_pending,
              data.add_tasks_pending
            )}</div></div>
            <div><div class="stat-label">错误</div><div class="stat-value text-red">${formatWithDelta(
              data.tasks_failed,
              data.add_tasks_failed
            )}</div></div>
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

function formatWithDelta(value, delta) {
  if (!delta || delta === 0) {
    return `${value}`;
  }
  const sign = delta > 0 ? "+" : "-";
  return `${value}<small style="color: ${
    delta > 0 ? "green" : "red"
  }; margin-left: 4px;">${sign}${Math.abs(delta)}</small>`;
}

function updateSummary() {
  let processed = 0,
    pending = 0,
    error = 0,
    active = 0;
  Object.values(nodeStatuses).forEach((s) => {
    processed += s.tasks_processed;
    pending += s.tasks_pending;
    error += s.tasks_failed;
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
  const previousValue = nodeFilter.value; // 记住当前选中值

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
    nodeFilter.value = ""; // 默认选“全部节点”
  }
}

function initChart() {
  const ctx = document.getElementById("node-progress-chart").getContext("2d");
  progressChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [],
    },
    options: {
      animation: false, // 直接关掉所有动画
      responsive: true,
      plugins: {
        legend: {
          display: true,
          onClick: (e, legendItem, legend) => {
            const index = legendItem.datasetIndex;
            const nodeName = progressChart.data.datasets[index].label;

            // 更新隐藏集合
            if (hiddenNodes.has(nodeName)) {
              hiddenNodes.delete(nodeName);
            } else {
              hiddenNodes.add(nodeName);
            }

            // 持久化保存到 localStorage
            localStorage.setItem(
              "hiddenNodes",
              JSON.stringify([...hiddenNodes])
            );

            // 继续默认 Chart.js 的隐藏逻辑
            const meta = legend.chart.getDatasetMeta(index);
            meta.hidden =
              meta.hidden === null
                ? !legend.chart.data.datasets[index].hidden
                : null;
            legend.chart.update();
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
      scales: {
        x: { display: true, title: { display: true, text: "时间" } },
        y: { display: true, title: { display: true, text: "完成任务数" } },
      },
    },
  });
}

function updateChartData(nodeDataMap) {
  const datasets = Object.entries(nodeDataMap).map(([node, data], index) => ({
    label: node,
    data: data,
    borderColor: getColor(index),
    fill: false,
    tension: 0.3,
    hidden: hiddenNodes.has(node), // 根据用户之前的选择
  }));

  const firstNode = Object.keys(nodeDataMap)[0];
  progressChart.data.labels = nodeDataMap[firstNode]?.map((p) =>
    new Date(p.x * 1000).toLocaleTimeString()
  );
  progressChart.data.datasets = datasets;

  progressChart.update();
}

function getColor(index) {
  const colors = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#ec4899",
    "#22c55e",
    "#0ea5e9",
    "#f97316",
  ];
  return colors[index % colors.length];
}

function extractProgressData(nodeStatuses) {
  const result = {};
  for (const [node, data] of Object.entries(nodeStatuses)) {
    if (data.history) {
      result[node] = data.history.map((point) => ({
        x: point.timestamp,
        y: point.tasks_processed,
      }));
    }
  }
  return result;
}

// 简单移动端判断
function isMobile() {
  return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}
