let nodes = [];
let selectedNodes = [];
let currentInputMethod = "json";
let uploadedFile = null;

const exampleTask = {
  task_id: "task_001",
  task_name: "数据处理任务",
  priority: "high",
  parameters: {
    input_source: "/data/input.csv",
    output_path: "/data/output/",
    batch_size: 1000,
    timeout: 3600,
  },
  schedule: {
    type: "immediate",
    retry_count: 3,
  },
};

document.addEventListener("DOMContentLoaded", async function () {
  renderNodeList();
  setupEventListeners();
});

function setupEventListeners() {
  document
    .getElementById("search-input")
    .addEventListener("input", function (e) {
      renderNodeList(e.target.value);
    });

  document
    .getElementById("json-textarea")
    .addEventListener("input", function (e) {
      validateJSON(e.target.value);
    });

  document
    .getElementById("file-input")
    .addEventListener("change", handleFileUpload);
}

function renderNodeList(searchTerm = "") {
  const nodeListHTML = Object.keys(nodeStatuses)
    .map(
      (nodeName) => `
        <div class="node-item" onclick="selectNode('${nodeName}')">
          <div class="node-info">
            <div class="node-name">${nodeName}</div>
          </div>
          <span class="badge ${
            nodeStatuses[nodeName].active ? "badge-success" : "badge-inactive"
              }">
              ${nodeStatuses[nodeName].active ? "运行中" : "未运行"}
          </span>
        </div>`
    )
    .join("");

  document.getElementById("node-list").innerHTML = nodeListHTML;
}

function selectNode(nodeName) {
  const node = {
    name: nodeName,
    type: nodeStatuses[nodeName].execution_mode || "unknown",
  };

  selectedNodes = [node];
  console.log("选中的节点列表:", selectedNodes);
  updateSelectedNodes();
}

function removeNode(nodeName) {
  selectedNodes = selectedNodes.filter((n) => n.name !== nodeName);
  updateSelectedNodes();
}

function updateSelectedNodes() {
  const selectedSection = document.getElementById("selected-section");
  const selectedList = document.getElementById("selected-list");
  const selectedCount = document.getElementById("selected-count");

  if (selectedNodes.length === 0) {
    selectedSection.style.display = "none";
    return;
  }

  selectedSection.style.display = "block";
  selectedCount.textContent = selectedNodes.length;

  const selectedHTML = selectedNodes
    .map(
      (node) => `
        <div class="selected-item">
          <span class="selected-name">${node.name}</span>
          <button class="remove-btn" onclick="removeNode('${node.name}')">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>`
    )
    .join("");

  selectedList.innerHTML = selectedHTML;
}

function selectAllNodes() {
  const searchTerm = document.getElementById("search-input").value;
  const filteredNodes = nodes.filter((node) =>
    node.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  filteredNodes.forEach((node) => {
    if (!selectedNodes.find((n) => n.name === node.name)) {
      selectedNodes.push(node);
    }
  });

  updateSelectedNodes();
}

function clearSelection() {
  selectedNodes = [];
  updateSelectedNodes();
}

function switchInputMethod(method) {
  currentInputMethod = method;

  document
    .getElementById("json-toggle")
    .classList.toggle("active", method === "json");
  document
    .getElementById("file-toggle")
    .classList.toggle("active", method === "file");

  document
    .getElementById("json-input-section")
    .classList.toggle("hidden", method !== "json");
  document
    .getElementById("file-input-section")
    .classList.toggle("hidden", method !== "file");
}

function fillExample() {
  document.getElementById("json-textarea").value = JSON.stringify(
    exampleTask,
    null,
    2
  );
  hideError("json-error");
}

function validateJSON(text) {
  if (!text.trim()) {
    hideError("json-error");
    return true;
  }

  try {
    JSON.parse(text);
    hideError("json-error");
    return true;
  } catch (e) {
    showError("json-error", "JSON 格式不合法");
    return false;
  }
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  if (!file.name.endsWith(".json")) {
    showError("file-error", "请上传 .json 格式的文件");
    return;
  }

  const reader = new FileReader();
  reader.onload = function (event) {
    try {
      const content = event.target.result;
      JSON.parse(content);

      uploadedFile = { name: file.name, content };
      document.getElementById("file-name").textContent = `已上传: ${file.name}`;
      document.getElementById("file-info").style.display = "flex";
      hideError("file-error");
    } catch (e) {
      showError("file-error", "上传文件无效，请检查JSON格式");
      uploadedFile = null;
      document.getElementById("file-info").style.display = "none";
    }
  };
  reader.readAsText(file);
}

function showError(elementId, message) {
  const errorDiv = document.getElementById(elementId);
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function hideError(elementId) {
  document.getElementById(elementId).style.display = "none";
}

function showStatus(message, isSuccess = false) {
  const statusDiv = document.getElementById("status-message");
  const iconSVG = isSuccess
    ? '<svg class="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    : '<svg class="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';

  statusDiv.innerHTML = iconSVG + message;
  statusDiv.className = `status-message ${
    isSuccess ? "status-success" : "status-error"
  }`;
  statusDiv.style.visibility = "visible";

  setTimeout(() => {
    statusDiv.style.visibility = "hidden";
  }, 3000);
}

async function handleSubmit() {
  if (selectedNodes.length === 0) {
    showStatus("请选择至少一个节点", false);
    return;
  }

  let taskData;
  if (currentInputMethod === "json") {
    const jsonText = document.getElementById("json-textarea").value.trim();
    if (!jsonText) {
      showStatus("请输入任务数据", false);
      return;
    }
    if (!validateJSON(jsonText)) {
      showStatus("JSON格式不合法", false);
      return;
    }
    taskData = JSON.parse(jsonText);
  } else {
    if (!uploadedFile) {
      showStatus("请上传任务文件", false);
      return;
    }
    taskData = JSON.parse(uploadedFile.content);
  }

  setButtonLoading(true);

  try {
    const response = await fetch("/api/push_task_injection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        node: selectedNodes[0].name,
        task_datas: taskData,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    showStatus("任务注入成功", true);
    clearForm();
  } catch (e) {
    console.error(e);
    showStatus("任务注入失败，请重试", false);
  } finally {
    setButtonLoading(false);
  }
}

function setButtonLoading(loading) {
  const btn = document.getElementById("submit-btn");
  if (loading) {
    btn.innerHTML = '<div class="spinner"></div>提交中...';
    btn.disabled = true;
  } else {
    btn.innerHTML = "提交任务注入";
    btn.disabled = false;
  }
}

function clearForm() {
  selectedNodes = [];
  updateSelectedNodes();
  document.getElementById("json-textarea").value = "";
  hideError("json-error");
  document.getElementById("file-input").value = "";
  uploadedFile = null;
  document.getElementById("file-info").style.display = "none";
  hideError("file-error");
  document.getElementById("search-input").value = "";
  renderNodeList();
}
