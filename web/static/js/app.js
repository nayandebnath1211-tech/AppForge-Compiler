// --- APP CONTROLLER STATE ---
let currentConfig = null;
let currentRoute = "/dashboard";
let selectedSchemaTab = "db";
let isCompiling = false;

// Preset prompt mapping to fill prompt text
const PRESET_PROMPTS = {
    "prod-1": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "prod-2": "Build an e-commerce app with product listings, search, shopping cart, checkout, payments, and order history. Sellers can manage products, admins can see sales metrics.",
    "prod-3": "Build a project board like Trello with columns, tasks, assignees, comments, drag-and-drop simulation, and premium tier for unlimited boards.",
    "prod-4": "Build a support ticketing system with customer portal, agent view, ticket assignment, status tracking, SLA logic, and admin reporting.",
    "prod-5": "Build a hotel booking platform with search, room availability check, booking creation, payments, and admin room management.",
    "prod-6": "Build an API analytics tracker with request logger, dashboard showing response times, usage limits gating for free tier, and alert setup.",
    "prod-7": "Build a workout app with exercise log, routine planner, progress charts, premium personal trainer chat feature, and user profile.",
    "prod-8": "Build a library book management app with borrow/return tracking, fine payments, search by author/genre, and librarian dashboard.",
    "prod-9": "Build a social media post scheduler with draft creation, queue preview, premium automatic posting simulation, and content category analytics.",
    "prod-10": "Build an inventory management system with stock level tracking, low stock alerts, supplier information, purchase order approvals, and role access.",
    "edge-1": "Make a website for a store where people do things.",
    "edge-2": "Build a public database where anyone can read all messages, but make sure only the sender and admin can see them.",
    "edge-3": "Make an app with payment integration and user roles.",
    "edge-4": "Create a dashboard for premium subscribers only, but it should be free and accessible to guests without signing in.",
    "edge-5": "An app for managing items with some analytics.",
    "edge-6": "Build a dashboard.",
    "edge-7": "A secure messaging app where messages are fully encrypted and stored in DB, but admins can edit any user's messages directly in the dashboard.",
    "edge-8": "Make a booking system.",
    "edge-9": "Build a system that tracks stuff for a company.",
    "edge-10": "Build an e-commerce cart where users can buy items for free, but it must process payments for each checkout."
};

// --- INITIALIZE PAGE ---
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initPresets();
    initCompiler();
    initSandbox();
    initEvaluation();
    
    // Load existing evaluation report on startup
    loadEvaluationReport();
});

// --- TABS ROUTING ---
function initTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            
            // Toggle active button
            tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Toggle active content
            const contents = document.querySelectorAll(".tab-content");
            contents.forEach(c => c.classList.remove("active"));
            document.getElementById(tabId).classList.add("active");
            
            // Special triggers on tab open
            if (tabId === "dbTab") {
                refreshDatabaseInspector();
            }
        });
    });

    // Schema viewer sidebar navigation
    const schemaNavBtns = document.querySelectorAll(".schema-nav-btn");
    schemaNavBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            schemaNavBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            selectedSchemaTab = btn.getAttribute("data-schema");
            displaySchemaJSON();
        });
    });

    // Copy schema functionality
    document.getElementById("copySchemaBtn").addEventListener("click", () => {
        const text = document.getElementById("schemaCode").innerText;
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById("copySchemaBtn");
            btn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
            setTimeout(() => {
                btn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy JSON`;
            }, 2000);
        });
    });
}

// --- PRESET PROMPTS ---
function initPresets() {
    const promptSelect = document.getElementById("promptSelect");
    const instructionInput = document.getElementById("instructionInput");

    promptSelect.addEventListener("change", () => {
        const selectedVal = promptSelect.value;
        if (PRESET_PROMPTS[selectedVal]) {
            instructionInput.value = PRESET_PROMPTS[selectedVal];
        }
    });

    // Key input mode badge check
    const apiKeyInput = document.getElementById("apiKeyInput");
    const modeBadge = document.getElementById("modeBadge");
    
    const updateModeBadge = () => {
        if (apiKeyInput.value.trim().length > 0) {
            modeBadge.classList.add("live-active");
            modeBadge.querySelector(".badge-text").innerText = "LLM Engine Active";
        } else {
            modeBadge.classList.remove("live-active");
            modeBadge.querySelector(".badge-text").innerText = "Mock Mode Active";
        }
    };

    apiKeyInput.addEventListener("input", updateModeBadge);
}

// --- PIPELINE COMPILER ---
function initCompiler() {
    const compileBtn = document.getElementById("compileBtn");
    const instructionInput = document.getElementById("instructionInput");
    const apiKeyInput = document.getElementById("apiKeyInput");

    compileBtn.addEventListener("click", async () => {
        const prompt = instructionInput.value.trim();
        if (!prompt || isCompiling) return;

        isCompiling = true;
        compileBtn.disabled = true;
        compileBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Compiling...`;
        
        // Reset pipeline visualizer
        resetPipelineConsole();
        setPipelineStatus("compiling", "Generating");

        // UI stage animation simulation
        await animatePipelineStage("step1", "latency1", 800, "Extracting entities and roles...");
        await animatePipelineStage("step2", "latency2", 800, "Mapping DB structures and API routes...");
        await animatePipelineStage("step3", "latency3", 600, "Generating strict JSON configurations...");
        
        // Actually call backend
        try {
            const res = await fetch("/api/compile", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    prompt: prompt,
                    api_key: apiKeyInput.value.trim()
                })
            });
            
            const data = await res.json();
            
            if (!res.ok) {
                throw new Error(data.error || "Compilation failed");
            }
            
            // Set compiler configuration
            currentConfig = data.config;
            
            // Update pipeline timings with real values
            updateStageTimings(data.metadata);
            
            // Final validation step representation
            const step4 = document.getElementById("step4");
            const details4 = document.getElementById("details4");
            const latency4 = document.getElementById("latency4");
            step4.classList.add("active");
            
            if (data.errors.length === 0) {
                step4.className = "pipeline-step completed";
                latency4.innerText = `${data.metadata.repair_log.length} retries`;
                details4.innerHTML = `<span style="color: var(--success)"><i class="fa-solid fa-circle-check"></i> Validation passed successfully. 0 mismatches found.</span>`;
            } else {
                step4.className = "pipeline-step failed";
                latency4.innerText = `${data.metadata.retries} retries`;
                let errorMsgs = data.errors.map(e => `<li>[${e.category}] ${e.message}</li>`).join("");
                details4.innerHTML = `
                    <span style="color: var(--danger)"><i class="fa-solid fa-triangle-exclamation"></i> Validation failed:</span>
                    <ul style="padding-left: 1.25rem; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
                        ${errorMsgs}
                    </ul>
                `;
            }
            
            setPipelineStatus("success-state", "Finished");
            
            // Enable Sandbox elements
            enableSandbox();
            
            // Mount app starting at /dashboard
            currentRoute = "/dashboard";
            loadSandboxPage(currentRoute);
            
        } catch (err) {
            console.error(err);
            setPipelineStatus("idled", "Error");
            const activeStep = document.querySelector(".pipeline-step.active") || document.getElementById("step4");
            activeStep.className = "pipeline-step failed";
            activeStep.querySelector(".step-details").innerHTML = `<span style="color: var(--danger)"><i class="fa-solid fa-circle-xmark"></i> ${err.message}</span>`;
        } finally {
            isCompiling = false;
            compileBtn.disabled = false;
            compileBtn.innerHTML = `<i class="fa-solid fa-gears"></i> Compile App Schema`;
        }
    });
}

function resetPipelineConsole() {
    const steps = ["step1", "step2", "step3", "step4"];
    steps.forEach(id => {
        const el = document.getElementById(id);
        el.className = "pipeline-step";
        el.querySelector(".step-indicator").innerHTML = `<i class="fa-regular fa-circle"></i>`;
        el.querySelector(".step-latency").innerText = "-";
    });
    document.getElementById("details1").innerText = "Parses prompt into structured user intent.";
    document.getElementById("details2").innerText = "Outlines database tables mapping, route permissions, and workflow logic.";
    document.getElementById("details3").innerText = "Compiles designs into strict configurations.";
    document.getElementById("details4").innerText = "Verifies cross-layer consistency and executes correction loops.";
}

function setPipelineStatus(stateClass, label) {
    const badge = document.getElementById("overallPipelineStatus");
    badge.className = `pipeline-status-badge ${stateClass}`;
    badge.innerText = label;
}

function animatePipelineStage(stepId, latencyId, duration, processingText) {
    return new Promise(resolve => {
        const step = document.getElementById(stepId);
        step.classList.add("active");
        step.querySelector(".step-indicator").innerHTML = `<i class="fa-solid fa-circle-notch"></i>`;
        step.querySelector(".step-details").innerText = processingText;
        
        setTimeout(() => {
            step.className = "pipeline-step completed";
            step.querySelector(".step-indicator").innerHTML = `<i class="fa-solid fa-circle-check"></i>`;
            resolve();
        }, duration);
    });
}

function updateStageTimings(metadata) {
    // Stage 1
    const stage1 = metadata.stages.find(s => s.name === "Intent Extraction");
    if (stage1) {
        document.getElementById("latency1").innerText = `${stage1.latency_ms}ms`;
        document.getElementById("details1").innerText = "Intent extraction completed. Entities parsed.";
    }
    // Stage 2
    const stage2 = metadata.stages.find(s => s.name === "System Design Layer");
    if (stage2) {
        document.getElementById("latency2").innerText = `${stage2.latency_ms}ms`;
        document.getElementById("details2").innerText = "System Design blueprint drafted successfully.";
    }
    // Stage 3
    const stage3 = metadata.stages.find(s => s.name === "Schema Generation");
    if (stage3) {
        document.getElementById("latency3").innerText = `${stage3.latency_ms}ms`;
        document.getElementById("details3").innerText = "AppConfig schemas generated and type-enforced.";
    }
}

// --- INTERACTIVE SANDBOX PREVIEW ---
function initSandbox() {
    const roleSelect = document.getElementById("simulateRole");
    const browserReloadBtn = document.getElementById("browserReloadBtn");
    const clearLogsBtn = document.getElementById("clearAuditLogsBtn");

    roleSelect.addEventListener("change", async () => {
        const role = roleSelect.value;
        let subscription = "free";
        if (role === "PremiumMember") {
            subscription = "premium";
        }
        
        try {
            const res = await fetch("/api/simulator/user", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({role: role, subscription: subscription})
            });
            const data = await res.json();
            updateSessionBox(data.user);
            
            // Reload page with new session
            loadSandboxPage(currentRoute);
        } catch (err) {
            console.error("Failed to switch session", err);
        }
    });

    browserReloadBtn.addEventListener("click", () => {
        loadSandboxPage(currentRoute);
    });

    clearLogsBtn.addEventListener("click", () => {
        document.getElementById("sandboxLogs").innerHTML = `<p class="log-entry log-system">Audit logs cleared.</p>`;
    });
}

function enableSandbox() {
    document.getElementById("simulateRole").disabled = false;
    document.getElementById("browserReloadBtn").disabled = false;
    document.getElementById("refreshDbBtn").disabled = false;
    
    // Set initial session to Member
    document.getElementById("simulateRole").value = "Member";
    updateSessionBox({
        id: 2,
        email: "member@appforge.com",
        role: "Member",
        subscription: "free"
    });
    
    // Display schemas
    displaySchemaJSON();
}

function updateSessionBox(user) {
    const box = document.getElementById("sessionInfoBox");
    box.querySelector(".session-status").innerText = user.id ? "Authenticated" : "Guest Mode";
    box.querySelector(".session-status").style.color = user.id ? "var(--success)" : "var(--warning)";
    
    document.getElementById("sessUserId").innerText = user.id || "None";
    document.getElementById("sessUserEmail").innerText = user.email;
    
    const tierBadge = document.getElementById("sessUserTier");
    tierBadge.innerText = user.subscription;
    tierBadge.className = `badge ${user.subscription}`;
}

async function loadSandboxPage(route) {
    currentRoute = route;
    document.getElementById("browserUrlBar").value = `http://localhost:8080${route}`;
    
    const screen = document.getElementById("browserScreen");
    screen.innerHTML = `<div class="sandbox-placeholder"><i class="fa-solid fa-spinner fa-spin"></i><p>Rendering simulated components...</p></div>`;

    try {
        const res = await fetch(`/api/simulator/page?route=${encodeURIComponent(route)}`);
        const data = await res.json();
        
        if (res.status === 401 || data.status === 401) {
            renderGatedScreen("Unauthorized", "You must log in to access this page. Select a role on the left sidebar panel to switch sessions.");
            return;
        }
        if (res.status === 403 || data.status === 403) {
            renderGatedScreen("Access Denied", "Your active user role does not have permission to view this page. Switch to an 'Admin' role in the Controller.");
            return;
        }
        if (data.status === 404) {
            renderGatedScreen("404 Not Found", data.error);
            return;
        }

        renderAppShell(data);
        
    } catch (err) {
        screen.innerHTML = `<div class="sandbox-placeholder"><i class="fa-solid fa-circle-xmark" style="color: var(--danger)"></i><p>Simulation error: ${err.message}</p></div>`;
    } finally {
        // Sync logs and SQLite database
        fetchAuditLogs();
        refreshDatabaseInspector();
    }
}

function renderGatedScreen(title, message) {
    const screen = document.getElementById("browserScreen");
    screen.innerHTML = `
        <div class="sim-gated-screen">
            <i class="fa-solid fa-shield-halved"></i>
            <h3>${title}</h3>
            <p>${message}</p>
        </div>
    `;
}

function renderAppShell(data) {
    const screen = document.getElementById("browserScreen");
    screen.innerHTML = "";

    const shell = document.createElement("div");
    shell.className = "sim-app-shell";

    // App Sidebar Navigation
    const sidebar = document.createElement("div");
    sidebar.className = "sim-sidebar";
    
    const title = document.createElement("div");
    sidebar.className = "sim-sidebar";
    sidebar.innerHTML = `<div class="sim-sidebar-title">${currentConfig ? currentConfig.app_name : "Workspace"}</div>`;
    
    // Add nav links
    if (currentConfig && currentConfig.ui_schema) {
        currentConfig.ui_schema.pages.forEach(p => {
            const nav = document.createElement("a");
            nav.className = `sim-nav-item ${p.route === currentRoute ? 'active' : ''}`;
            
            // Select icon based on page name
            let icon = "fa-chart-pie";
            if (p.name.toLowerCase().includes("contact")) icon = "fa-address-book";
            else if (p.name.toLowerCase().includes("bill") || p.name.toLowerCase().includes("pay")) icon = "fa-credit-card";
            else if (p.name.toLowerCase().includes("list") || p.name.toLowerCase().includes("shop")) icon = "fa-cart-shopping";
            else if (p.name.toLowerCase().includes("analy") || p.name.toLowerCase().includes("metric")) icon = "fa-chart-line";
            
            nav.innerHTML = `<i class="fa-solid ${icon}"></i> ${p.name}`;
            nav.addEventListener("click", () => loadSandboxPage(p.route));
            sidebar.appendChild(nav);
        });
    }
    shell.appendChild(sidebar);

    // Dynamic Content Area
    const content = document.createElement("div");
    content.className = "sim-content";
    
    const contentHeader = document.createElement("div");
    contentHeader.className = "sim-page-header";
    contentHeader.innerHTML = `
        <h2>${data.page_name}</h2>
        <small style="color: var(--text-muted)">Layout: ${data.layout}</small>
    `;
    content.appendChild(contentHeader);

    // Render Components Grid
    const grid = document.createElement("div");
    grid.className = "sim-grid-layout";
    if (data.components.length > 1) {
        grid.classList.add("split-grid");
    }

    data.components.forEach(comp => {
        const compEl = renderComponent(comp);
        grid.appendChild(compEl);
    });
    
    content.appendChild(grid);
    shell.appendChild(content);
    screen.appendChild(shell);
}

function renderComponent(comp) {
    const card = document.createElement("div");
    card.className = "sim-comp-card";
    card.innerHTML = `<h4>${comp.title}</h4>`;

    if (comp.props && comp.props.error) {
        card.innerHTML += `<div style="color: var(--danger); font-size: 0.75rem;"><i class="fa-solid fa-triangle-exclamation"></i> Gated Trigger: ${comp.props.error}</div>`;
        return card;
    }

    // 1. STAT CARD COMPONENT
    if (comp.type === "StatCard") {
        const p = document.createElement("p");
        p.style.fontSize = "0.8rem";
        p.style.color = "var(--text-secondary)";
        p.style.lineHeight = "1.5";
        p.innerText = comp.props.text || "";
        card.appendChild(p);
    }
    
    // 2. HEADING COMPONENT
    else if (comp.type === "Heading") {
        const p = document.createElement("p");
        p.style.fontSize = "0.8rem";
        p.style.color = "var(--text-secondary)";
        p.innerText = comp.props.text || "";
        card.appendChild(p);
    }

    // 3. TABLE COMPONENT
    else if (comp.type === "Table") {
        const tableWrapper = document.createElement("div");
        tableWrapper.className = "sim-table-wrapper";

        const table = document.createElement("table");
        table.className = "sim-table";

        // Headers
        const cols = comp.props.columns || ["id", "name"];
        const thead = document.createElement("thead");
        const trHeader = document.createElement("tr");
        cols.forEach(c => {
            const th = document.createElement("th");
            th.innerText = c.toUpperCase();
            trHeader.appendChild(th);
        });
        thead.appendChild(trHeader);
        table.appendChild(thead);

        // Body rows
        const tbody = document.createElement("tbody");
        const rows = comp.props.table_data || [];
        
        if (rows.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.setAttribute("colspan", cols.length);
            td.style.textAlign = "center";
            td.style.color = "var(--text-muted)";
            td.innerText = "No records found.";
            tr.appendChild(td);
            tbody.appendChild(tr);
        } else {
            rows.forEach(row => {
                const tr = document.createElement("tr");
                cols.forEach(c => {
                    const td = document.createElement("td");
                    td.innerText = row[c] !== undefined ? row[c] : "-";
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }
        table.appendChild(tbody);
        tableWrapper.appendChild(table);
        card.appendChild(tableWrapper);
    }

    // 4. FORM COMPONENT
    else if (comp.type === "Form") {
        const form = document.createElement("form");
        const fields = comp.props.fields || [];

        fields.forEach(f => {
            const grp = document.createElement("div");
            grp.className = "sim-form-group";
            grp.innerHTML = `
                <label>${f.label || f.name}</label>
                <input type="${f.type === 'email' ? 'email' : 'text'}" name="${f.name}" required>
            `;
            form.appendChild(grp);
        });

        // Add Submit Button
        const btnWrapper = document.createElement("div");
        btnWrapper.style.marginTop = "1rem";
        
        const btn = document.createElement("button");
        btn.type = "submit";
        btn.className = "btn btn-primary btn-sm";
        btn.innerText = comp.title.includes("Contact") ? "Add Contact Lead" : "Submit Query";
        btnWrapper.appendChild(btn);
        form.appendChild(btnWrapper);

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const payload = {};
            formData.forEach((v, k) => payload[k] = v);

            // Execute the action bound to form submit (action index 0)
            btn.disabled = true;
            btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing...`;
            
            try {
                const res = await fetch("/api/simulator/action", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        route: currentRoute,
                        component_id: comp.id,
                        action_index: 0,
                        payload: payload
                    })
                });
                const data = await res.json();
                
                if (data.status === 200) {
                    form.reset();
                    // Alert success
                    alert("Operation successful! Record written to SQLite.");
                    loadSandboxPage(currentRoute);
                } else {
                    alert(`Error: ${data.body.error || "Gated Action Blocked"}`);
                    loadSandboxPage(currentRoute);
                }
            } catch (err) {
                alert(`Error executing action: ${err.message}`);
            } finally {
                btn.disabled = false;
                btn.innerText = "Submit Query";
            }
        });

        card.appendChild(form);
    }

    // 5. CHART COMPONENT
    else if (comp.type === "Chart") {
        const chartWrapper = document.createElement("div");
        chartWrapper.style.marginTop = "1rem";
        
        const chartData = comp.props.chart_data || [];
        
        if (chartData.length === 0) {
            chartWrapper.innerHTML = `
                <div style="color: var(--text-muted); font-size: 0.75rem; text-align: center; padding: 1.5rem 0;">
                    No chart metrics available. Add deals to visualize metrics.
                </div>
            `;
        } else {
            // Render simple simulated bar charts
            let barsHtml = chartData.map(item => {
                const title = item.title || item.name || "Deal";
                const amount = item.amount || 1000;
                // Calculate percentage relative to max amount or limit
                const pct = Math.min((amount / 20000) * 100, 100);
                return `
                    <div style="margin-bottom: 0.75rem;">
                        <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:var(--text-secondary); margin-bottom:0.2rem;">
                            <span>${title}</span>
                            <span style="font-family:var(--font-mono)">$${amount}</span>
                        </div>
                        <div style="background:rgba(255,255,255,0.03); height:8px; border-radius:4px; overflow:hidden;">
                            <div style="background:var(--primary); width:${pct}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>
                `;
            }).join("");
            chartWrapper.innerHTML = barsHtml;
        }
        card.appendChild(chartWrapper);
    }

    // 6. BUTTON COMPONENT
    else if (comp.type === "Button") {
        const btn = document.createElement("button");
        btn.className = `btn btn-primary btn-sm`;
        if (comp.props.variant === "success") btn.className = "btn btn-primary btn-sm"; // matches success hue in styled CSS
        btn.innerText = comp.title;
        
        btn.addEventListener("click", async () => {
            btn.disabled = true;
            try {
                const res = await fetch("/api/simulator/action", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        route: currentRoute,
                        component_id: comp.id,
                        action_index: 0,
                        payload: {}
                    })
                });
                const data = await res.json();
                
                if (data.action_type === "navigate") {
                    loadSandboxPage(data.target);
                } else if (data.action_type === "api_call") {
                    if (data.status === 200) {
                        alert("Billing action successful! Upgraded to Premium Tier.");
                        // Reload role
                        const roleSelect = document.getElementById("simulateRole");
                        roleSelect.value = "PremiumMember";
                        roleSelect.dispatchEvent(new Event("change"));
                    } else {
                        alert(`Action failed: ${data.body.error}`);
                    }
                }
            } catch (err) {
                console.error("Action error", err);
            } finally {
                btn.disabled = false;
            }
        });
        card.appendChild(btn);
    }

    return card;
}

async function fetchAuditLogs() {
    try {
        const res = await fetch("/api/simulator/logs");
        const data = await res.json();
        
        const logsBox = document.getElementById("sandboxLogs");
        logsBox.innerHTML = "";
        
        data.logs.forEach(log => {
            const p = document.createElement("p");
            let cls = "log-system";
            if (log.category === "NAVIGATE") cls = "log-navigate";
            else if (log.category === "UI_ACTION") cls = "log-action";
            else if (log.category === "SQL_EXEC") cls = "log-sql";
            else if (log.category === "API_RESPONSE" || log.category === "API_BIND") cls = "log-api";
            else if (log.category === "UI_GATE") cls = "log-err";
            
            p.className = `log-entry ${cls}`;
            p.innerHTML = `[${log.category}] ${log.message} ${log.details ? '<br><span style="padding-left:1rem; opacity:0.6;">Body: ' + JSON.stringify(log.details) + '</span>' : ''}`;
            logsBox.appendChild(p);
        });
        
        // Scroll to bottom
        logsBox.scrollTop = logsBox.scrollHeight;
    } catch (err) {
        console.error("Failed to fetch logs", err);
    }
}

// --- DATABASE INSPECTOR ---
async function refreshDatabaseInspector() {
    const layout = document.getElementById("dbInspectorLayout");
    if (!currentConfig) {
        return; // keeps placeholder active
    }

    try {
        const res = await fetch("/api/simulator/db-inspect");
        const data = await res.json();
        
        if (data.error) {
            layout.innerHTML = `<div class="db-placeholder"><i class="fa-solid fa-triangle-exclamation" style="color:var(--danger)"></i><h3>Inspector Error</h3><p>${data.error}</p></div>`;
            return;
        }

        layout.innerHTML = "";
        
        const tables = data.tables || {};
        const tableNames = Object.keys(tables);
        
        if (tableNames.length === 0) {
            layout.innerHTML = `<div class="db-placeholder"><h3>Database is empty</h3></div>`;
            return;
        }

        tableNames.forEach(tbl => {
            const section = document.createElement("div");
            section.className = "db-table-inspect";
            
            section.innerHTML = `
                <div class="db-table-title">
                    <i class="fa-solid fa-table"></i> TABLE: ${tbl} (${tables[tbl].length} rows)
                </div>
            `;
            
            const tableWrapper = document.createElement("div");
            tableWrapper.className = "sim-table-wrapper";
            
            const table = document.createElement("table");
            table.className = "sim-table";
            
            const rows = tables[tbl];
            if (rows.length === 0) {
                table.innerHTML = `<tbody><tr><td style="text-align:center; color:var(--text-muted);">Empty table</td></tr></tbody>`;
            } else {
                const cols = Object.keys(rows[0]);
                
                // Headers
                const thead = document.createElement("thead");
                const trH = document.createElement("tr");
                cols.forEach(c => {
                    const th = document.createElement("th");
                    th.innerText = c;
                    trH.appendChild(th);
                });
                thead.appendChild(trH);
                table.appendChild(thead);
                
                // Rows
                const tbody = document.createElement("tbody");
                rows.forEach(r => {
                    const tr = document.createElement("tr");
                    cols.forEach(c => {
                        const td = document.createElement("td");
                        td.innerText = r[c] !== null ? r[c] : "NULL";
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                table.appendChild(tbody);
            }
            
            tableWrapper.appendChild(table);
            section.appendChild(tableWrapper);
            layout.appendChild(section);
        });

    } catch (err) {
        layout.innerHTML = `<div class="db-placeholder"><i class="fa-solid fa-triangle-exclamation" style="color:var(--danger)"></i><h3>Inspector Connection Mismatch</h3><p>${err.message}</p></div>`;
    }
}

// --- TAB: SCHEMAS DISPLAY ---
function displaySchemaJSON() {
    if (!currentConfig) return;
    
    let schemaTitle = "db_schema.json";
    let schemaData = {};
    
    if (selectedSchemaTab === "db") {
        schemaTitle = "db_schema.json";
        schemaData = currentConfig.db_schema;
    } else if (selectedSchemaTab === "api") {
        schemaTitle = "api_schema.json";
        schemaData = currentConfig.api_schema;
    } else if (selectedSchemaTab === "ui") {
        schemaTitle = "ui_schema.json";
        schemaData = currentConfig.ui_schema;
    } else if (selectedSchemaTab === "auth") {
        schemaTitle = "auth_schema.json";
        schemaData = currentConfig.auth_schema;
    } else if (selectedSchemaTab === "logic") {
        schemaTitle = "logic_schema.json";
        schemaData = currentConfig.logic_schema;
    }

    document.getElementById("currentSchemaTitle").innerText = schemaTitle;
    document.getElementById("schemaCode").innerText = JSON.stringify(schemaData, null, 2);
}

// --- TAB: EVALUATION SYSTEM ---
function initEvaluation() {
    const runEvalBtn = document.getElementById("runEvalBtn");
    const apiKeyInput = document.getElementById("apiKeyInput");

    runEvalBtn.addEventListener("click", async () => {
        runEvalBtn.disabled = true;
        runEvalBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Evaluating 20 Prompts (Benchmark Running)...`;
        
        try {
            const res = await fetch("/api/evaluate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({api_key: apiKeyInput.value.trim()})
            });
            const report = await res.json();
            
            if (report.error) {
                alert(`Evaluation run failed: ${report.error}`);
            } else {
                renderEvaluationReport(report);
            }
        } catch (err) {
            alert(`Evaluation run failed: ${err.message}`);
        } finally {
            runEvalBtn.disabled = false;
            runEvalBtn.innerHTML = `<i class="fa-solid fa-play"></i> Trigger Full Evaluation Run (20 Prompts)`;
        }
    });
}

async function loadEvaluationReport() {
    try {
        const res = await fetch("/api/evaluate/results");
        const report = await res.json();
        
        if (!report.error) {
            renderEvaluationReport(report);
        }
    } catch (err) {
        console.log("No previous evaluation report found", err);
    }
}

function renderEvaluationReport(report) {
    document.getElementById("evalSuccessRate").innerText = `${report.success_rate}%`;
    document.getElementById("evalAvgLatency").innerText = `${report.average_latency_ms} ms`;
    document.getElementById("evalAvgRetries").innerText = `${report.average_retries}`;
    document.getElementById("evalTotalCost").innerText = `$${report.total_estimated_cost_usd}`;

    const list = document.getElementById("evalPromptsList");
    list.innerHTML = "";

    const allPrompts = [...report.results.products, ...report.results.edge_cases];
    allPrompts.forEach(p => {
        const item = document.createElement("div");
        item.className = "eval-prompt-item";
        
        item.innerHTML = `
            <div>
                <span class="name">${p.name}</span>
                <span class="latency" style="margin-left: 0.5rem">(${p.latency_ms}ms)</span>
                <div style="font-size:0.6rem; color:var(--text-muted); margin-top:0.15rem; max-width:280px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">
                    Prompt: "${p.prompt}"
                </div>
            </div>
            <div>
                <span class="status-badge ${p.success ? 'pass' : 'fail'}">${p.success ? 'PASS' : 'FAIL'}</span>
            </div>
        `;
        
        // Add click listener to load this evaluated prompt directly into compiler!
        item.style.cursor = "pointer";
        item.addEventListener("click", () => {
            document.getElementById("instructionInput").value = p.prompt;
            document.getElementById("promptSelect").value = p.id;
            
            // Switch to Sandbox/Compiler tab
            const tabButtons = document.querySelectorAll(".tab-btn");
            tabButtons[0].click(); // Click Sandbox tab
            
            alert(`Loaded prompt: "${p.name}". Click "Compile App Schema" to generate its sandbox!`);
        });

        list.appendChild(item);
    });
}
