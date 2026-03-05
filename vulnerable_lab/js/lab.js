// Vulnerable Lab Frontend
// This intentionally includes "vulnerable rendering modes" for learning.

const $ = (id) => document.getElementById(id);

function showTab(tabName) {
    document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));
    const el = $("tab-" + tabName);
    if (el) el.classList.remove("hidden");
}

document.querySelectorAll(".navbtn").forEach(btn => {
    btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

// Default tab
showTab("reflected");

// Health check
(async function healthCheck() {
    try {
        const r = await fetch("/api/health");
        const j = await r.json();
        $("healthPill").textContent = j.ok ? "Server OK" : "Server Error";
        $("healthPill").className = j.ok ? "pill ok" : "pill bad";
    } catch (e) {
        $("healthPill").textContent = "Offline";
        $("healthPill").className = "pill bad";
    }
})();

// ---------------------
// 1) Reflected XSS demo
// ---------------------
$("reflectedBtn").addEventListener("click", async () => {
    const q = $("reflectedInput").value || "";
    const safeMode = $("reflectedSafeToggle").checked;

    const r = await fetch("/api/reflected?q=" + encodeURIComponent(q));
    const j = await r.json();

    const out = $("reflectedOut");

    // Vulnerable render: uses innerHTML
    // Safe render: uses textContent
    if (!safeMode) {
        out.innerHTML = j.reflected; // intentionally vulnerable for learning
    } else {
        out.textContent = j.reflected; // safe
    }
});

// ---------------------
// 2) Stored XSS demo
// ---------------------
async function loadComments() {
    const safeMode = $("storedSafeToggle").checked;
    const r = await fetch("/api/comments");
    const j = await r.json();

    const container = $("commentsOut");
    container.innerHTML = "";

    j.comments.forEach(c => {
        const wrap = document.createElement("div");
        wrap.className = "item";

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.innerHTML = `<span><b>${escapeHtml(c.name)}</b></span><span>${c.created_at}</span>`;

        const body = document.createElement("div");

        // Vulnerable mode: render stored comment as HTML (XSS risk)
        // Safe mode: render as text only
        if (!safeMode) {
            body.innerHTML = c.comment; // intentionally vulnerable for learning
        } else {
            body.textContent = c.comment; // safe
        }

        wrap.appendChild(meta);
        wrap.appendChild(body);
        container.appendChild(wrap);
    });
}

$("addCommentBtn").addEventListener("click", async () => {
    const name = $("cName").value.trim();
    const comment = $("cText").value.trim();

    if (!name || !comment) {
        alert("Please enter name and comment.");
        return;
    }

    await fetch("/api/comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, comment })
    });

    $("cText").value = "";
    await loadComments();
});

$("storedSafeToggle").addEventListener("change", loadComments);

// Load initial comments
loadComments();

// ---------------------
// 3) DOM XSS demo
// ---------------------
function parseHash() {
    // Example hash: #msg=Hello
    const raw = (location.hash || "").replace(/^#/, "");
    const params = new URLSearchParams(raw);
    return params.get("msg") || "";
}

function renderHash() {
    const msg = parseHash();
    const safeMode = $("domSafeToggle").checked;
    const out = $("domOut");

    if (!safeMode) {
        // Vulnerable (DOM XSS style): innerHTML from URL hash
        out.innerHTML = msg; // intentionally vulnerable for learning
    } else {
        out.textContent = msg; // safe
    }
}

$("applyHashBtn").addEventListener("click", renderHash);
$("domSafeToggle").addEventListener("change", renderHash);

$("setHashBtn").addEventListener("click", () => {
    const v = $("hashInput").value.trim();
    location.hash = v ? "#" + v : "";
    renderHash();
});

// Render on load
renderHash();

// ---------------------
// 4) DB Users practice
// ---------------------
$("loadUsersBtn").addEventListener("click", async () => {
    const r = await fetch("/api/users");
    const j = await r.json();

    const container = $("usersOut");
    container.innerHTML = "";

    j.users.forEach(u => {
        const wrap = document.createElement("div");
        wrap.className = "item";
        wrap.innerHTML = `
      <div class="meta">
        <span><b>@${escapeHtml(u.username)}</b></span>
        <span>#${u.id}</span>
      </div>
      <div><span class="muted">Email:</span> ${escapeHtml(u.email)}</div>
      <div style="margin-top:6px">${escapeHtml(u.bio)}</div>
    `;
        container.appendChild(wrap);
    });
});

// helper: basic html escape used in some UI parts
function escapeHtml(s) {
    return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
