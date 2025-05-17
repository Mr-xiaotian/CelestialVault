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

document.addEventListener("DOMContentLoaded", async () => {
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

  // ✅ 只在页面加载时调用一次
  await loadStructure(); 

  refreshAll();
  refreshIntervalId = setInterval(refreshAll, refreshRate);
});

async function refreshAll() {
  await Promise.all([loadStatuses(), loadErrors()]);
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
    const res = await fetch('/api/structure');
    const structureText = await res.json();  // 结构是一个字符串数组
    const joined = structureText.join('\n');
    const data = parseStructureText(joined);
    renderTree(data);
  } catch (e) {
    console.error("结构加载失败", e);
  }
}

// 解析文本格式的任务结构并转换为树形数据结构
function parseStructureText(text) {
    // 移除顶部和底部边框
    const lines = text.trim().split('\n');
    const contentLines = lines.slice(1, lines.length - 1);
    
    // 解析行内容的正则表达式
    const stagePattern = /\| (\s*╘-->)?([^(]+) \(stage_mode: ([^,]+), func: ([^)]+)\)(.*?)\|$/;
    
    // 查找根节点
    const rootMatch = contentLines[0].match(stagePattern);
    if (!rootMatch) return null;
    
    const root = {
        stage_name: rootMatch[2].trim(),
        stage_mode: rootMatch[3].trim(),
        func_name: rootMatch[4].trim(),
        visited: rootMatch[5] && rootMatch[5].includes("already visited"),
        next_stages: []
    };
    
    // 记录当前的节点栈和层级
    const nodeStack = [{ node: root, level: 0 }];
    
    // 遍历剩余行
    for (let i = 1; i < contentLines.length; i++) {
        const line = contentLines[i];
        const match = line.match(stagePattern);
        
        if (match) {
            // 判断是否有前导箭头和缩进
            const hasArrow = match[1] !== undefined;
            if (!hasArrow) continue; // 跳过没有箭头的行
            
            // 计算缩进级别（计算前导空格数量 / 4）
            const indentText = match[1]; // 包含 ╘--> 的部分
            const indentLevel = (indentText.match(/\s/g) || []).length / 4 + 1;
            
            // 创建新节点
            const newNode = {
                stage_name: match[2].trim(),
                stage_mode: match[3].trim(),
                func_name: match[4].trim(),
                visited: match[5] && match[5].includes("already visited"),
                next_stages: []
            };
            
            // 找到正确的父节点
            // 当栈顶节点层级大于等于当前节点层级时，弹出栈顶
            while (nodeStack.length > 1 && nodeStack[nodeStack.length - 1].level >= indentLevel) {
                nodeStack.pop();
            }
            
            // 将新节点添加到父节点的子节点列表
            const parentNode = nodeStack[nodeStack.length - 1].node;
            parentNode.next_stages.push(newNode);
            
            // 将新节点压入栈
            nodeStack.push({ node: newNode, level: indentLevel });
        }
    }
    
    return root;
}

// 根据数据渲染树形结构
function renderTree(data) {
    const treeContainer = document.getElementById('task-tree');
    treeContainer.innerHTML = '';
    
    function buildTreeHTML(node, isLastChild = true) {
        let html = '<li>';
        
        // 添加节点内容
        html += `<div class="tree-node collapsible" onclick="toggleNode(this)">`;
        
        // 如果有子节点，添加展开/折叠图标
        if (node.next_stages && node.next_stages.length > 0) {
            html += `<span class="collapse-icon">-</span>`;
        }
        
        html += `<span class="stage-name">${node.stage_name}</span>`;
        html += `<span class="stage-mode">(stage_mode: ${node.stage_mode})</span>`;
        html += `<span class="stage-func">func: ${node.func_name}</span>`;
        
        if (node.visited) {
            html += `<span class="visited-mark">already visited</span>`;
        }
        
        html += '</div>';
        
        // 添加子节点
        if (node.next_stages && node.next_stages.length > 0) {
            html += '<ul>';
            node.next_stages.forEach((childNode, index) => {
                const isLast = index === node.next_stages.length - 1;
                html += buildTreeHTML(childNode, isLast);
            });
            html += '</ul>';
        }
        
        html += '</li>';
        return html;
    }
    
    const rootHTML = `<ul>${buildTreeHTML(data)}</ul>`;
    treeContainer.innerHTML = rootHTML;
    
    // 打印树的HTML结构到控制台，用于调试
    // console.log("树的HTML结构:", treeContainer.innerHTML);
}

// 切换节点展开/折叠
function toggleNode(element) {
    const childList = element.nextElementSibling;
    if (childList && childList.tagName === 'UL') {
        childList.classList.toggle('hidden');
        
        const icon = element.querySelector('.collapse-icon');
        if (icon) {
            icon.textContent = childList.classList.contains('hidden') ? '+' : '-';
        }
    }
}

// 切换主题
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
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
