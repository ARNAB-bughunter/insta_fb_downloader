// Language dropdown toggle
const langToggle = document.getElementById('langToggle');
const langDropdown = document.getElementById('langDropdown');
const backendUrl = `${window.location.protocol}//${window.location.hostname}:9191`;

langToggle.addEventListener('click', () => {
    langDropdown.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!langToggle.contains(e.target) && !langDropdown.contains(e.target)) {
        langDropdown.classList.remove('active');
    }
});

// Language dropdown items
langDropdown.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
        langDropdown.classList.remove('active');
    });
});

// URL input paste and clear
const urlInput = document.getElementById('urlInput');
const pasteBtn = document.getElementById('pasteBtn');
const clearBtn = document.getElementById('clearBtn');
const downloadBtn = document.getElementById('downloadButton');
const spinner = document.getElementById("spinner");
const icon = document.getElementById("downloadIcon");
const btnText = document.getElementById("btnText");

pasteBtn.addEventListener('click', async () => {
    try {
        const text = await navigator.clipboard.readText();
        urlInput.value = text;
        clearBtn.classList.remove('hidden');
    } catch (err) {
        console.error('Failed to read clipboard:', err);
    }
});

clearBtn.addEventListener('click', () => {
    urlInput.value = '';
    clearBtn.classList.add('hidden');
});

urlInput.addEventListener('input', () => {
    if (urlInput.value) {
        clearBtn.classList.remove('hidden');
    } else {
        clearBtn.classList.add('hidden');
    }
});

downloadBtn.addEventListener("click", async () => {
    const inputUrl = urlInput.value?.trim();
    if (!inputUrl) return;

    // 🔄 Start loading UI
    downloadBtn.disabled = true;
    spinner.classList.remove("hidden");
    icon.classList.add("hidden");
    btnText.textContent = "Downloading...";

    try {
        /* 1️⃣ Call /download */
        const res = await fetch(`${backendUrl}/download`, {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: inputUrl })
        });

        if (!res.ok) throw new Error(`Download API failed: ${res.status}`);

        const data = await res.json();

        if (data.status !== "success" || !data.file_path) {
            throw new Error("Invalid download response");
        }

        /* 2️⃣ Call /files and trigger browser download */
        const encodedPath = encodeURIComponent(data.file_path);
        const fileUrl = `${backendUrl}/files?file_path=${encodedPath}`;

        // Create temporary anchor for download
        const a = document.createElement("a");
        a.href = fileUrl;
        a.download = data.file_path.split("/").pop(); // filename hint
        document.body.appendChild(a);
        a.click();
        a.remove();

    } catch (err) {
        console.error("Error:", err);
        alert("Download failed. Please try again.");
    } finally {
        // ✅ Reset UI
        downloadBtn.disabled = false;
        spinner.classList.add("hidden");
        icon.classList.remove("hidden");
        btnText.textContent = "Download";
    }
});



// Accordion functionality
function setupAccordion(containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const triggers = container.querySelectorAll('.accordion-trigger');

    triggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const targetId = trigger.getAttribute('data-target');
            const content = document.getElementById(targetId);
            const icon = trigger.querySelector('.accordion-icon');
            const isActive = content.classList.contains('active');

            // Close all other accordions in this container
            container.querySelectorAll('.accordion-content').forEach(c => {
                if (c !== content) {
                    c.classList.remove('active');
                }
            });

            container.querySelectorAll('.accordion-icon').forEach(i => {
                if (i !== icon) {
                    i.classList.remove('rotate-180');
                }
            });

            // Toggle current accordion
            if (isActive) {
                content.classList.remove('active');
                icon.classList.remove('rotate-180');
            } else {
                content.classList.add('active');
                icon.classList.add('rotate-180');
            }
        });
    });
}

// Initialize accordions
setupAccordion('#capabilitiesAccordion');
setupAccordion('#faqAccordion');

// Open first FAQ by default
const firstFaqIcon = document.querySelector('#faqAccordion .accordion-icon');
if (firstFaqIcon) {
    firstFaqIcon.classList.add('rotate-180');
}