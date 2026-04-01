/**
 * Smart Heating Insole Web App Logic
 */

const state = {
    isAutoMode: false,
    isConnected: false,
    shoeTemp: 24.5,
    outsideTemp: null,
    battery: 85,
    currentHeatLevel: 0,
    userProfile: 'daily',
    bleDevice: null,
    bleCharacteristic: null,
    overheating: false
};

const SAFE_TEMP_THRESHOLD = 45;
const FLASK_API_URL = "http://127.0.0.1:5002";

let autoModeInterval = null;
let mockBleInterval = null;

let el = {};

function init() {
    el = {
        modal: document.getElementById('first-launch-modal'),
        connectBtn: document.getElementById('ble-connect-btn'),
        batteryValue: document.getElementById('battery-value'),
        shoeTemp: document.getElementById('shoe-temp'),
        outsideTemp: document.getElementById('outside-temp'),
        modeSwitch: document.getElementById('mode-switch'),
        modeLabelManual: document.getElementById('mode-label-manual'),
        modeLabelAuto: document.getElementById('mode-label-auto'),
        manualControls: document.getElementById('manual-controls'),
        autoControls: document.getElementById('auto-controls'),
        heatButtons: document.querySelectorAll('.heat-btn'),
        heatBar: document.getElementById('heat-bar'),
        aiHeatLevel: document.getElementById('ai-heat-level'),
        profileButtons: document.querySelectorAll('.profile-btn'),
        warningBanner: document.getElementById('warning-banner')
    };

    bindEvents();
    updateUI();
    // startMockDeviceData();

    console.log("INIT DONE ✅");
}

/* ================= UI ================= */

function updateUI() {
    // Battery
    el.batteryValue.innerText = state.battery + "%";

    // Shoe temp
    // el.shoeTemp.innerText = state.shoeTemp.toFixed(1);  --- IGNORE --- (TEMP NOW COMES FROM fetchLiveTemp)

    // 🔥 FIXED OUTSIDE TEMP
    // 🔥 FINAL GUARANTEED FIX
if (state.outsideTemp !== null && state.outsideTemp !== undefined) {
    let temp = Number(state.outsideTemp);

    if (!isNaN(temp)) {
        el.outsideTemp.innerText = temp.toFixed(1);
    } else {
        el.outsideTemp.innerText = "--";
    }
} else {
    el.outsideTemp.innerText = "--";
}

    // Safety
    if (state.shoeTemp >= SAFE_TEMP_THRESHOLD) {
        state.overheating = true;
        el.warningBanner.classList.remove('hidden');
        setHeatLevel(0, true);
    } else {
        state.overheating = false;
        el.warningBanner.classList.add('hidden');
    }
}

function toggleModeUI() {
    if (state.isAutoMode) {
        el.modeLabelAuto.classList.add('active');
        el.modeLabelManual.classList.remove('active');
        el.manualControls.classList.add('hidden');
        el.autoControls.classList.remove('hidden');
        startAutoModePolling();
    } else {
        el.modeLabelAuto.classList.remove('active');
        el.modeLabelManual.classList.add('active');
        el.manualControls.classList.remove('hidden');
        el.autoControls.classList.add('hidden');
        stopAutoModePolling();
    }
}

function setHeatLevel(level, force = false) {
    if (state.overheating && level > 0 && !force) return;

    state.currentHeatLevel = level;

    el.heatBar.className = `level-${level}`;

    el.heatButtons.forEach(b => b.classList.remove('active'));
    const btn = document.querySelector(`.heat-btn[data-heat="${level}"]`);
    if (btn) btn.classList.add('active');

    el.aiHeatLevel.innerText = level + " (" + ['OFF','LOW','MED','HIGH'][level] + ")";
}

/* ================= EVENTS ================= */

function bindEvents() {
    el.modeSwitch.addEventListener('change', (e) => {
        state.isAutoMode = e.target.checked;
        toggleModeUI();
    });

    el.heatButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (state.isAutoMode) return;
            setHeatLevel(parseInt(e.currentTarget.dataset.heat));
        });
    });
}

/* ================= API ================= */

async function checkESP32Connection() {
    try {
        const res = await fetch("http://192.168.137.1:5002/latest");

        if (res.ok) {
            document.getElementById("esp-status").innerText = "🟢 Device Connected";
            document.getElementById("esp-status").style.color = "lightgreen";
        } else {
            throw new Error();
        }

    } catch (err) {
        document.getElementById("esp-status").innerText = "🔴 Not Connected";
        document.getElementById("esp-status").style.color = "red";
    }
}


function startAutoModePolling() {
    if (autoModeInterval) return;

    pollFlaskApi();
    autoModeInterval = setInterval(pollFlaskApi, 3000);
}

function stopAutoModePolling() {
    if (autoModeInterval) {
        clearInterval(autoModeInterval);
        autoModeInterval = null;
    }
}

async function pollFlaskApi() {
    try {
        const liveRes = await fetch("http://192.168.137.1:5002/latest");
        const liveData = await liveRes.json();

        const realTemp = liveData.shoe_temp;

        const res = await fetch(`${FLASK_API_URL}/predict?foot=${realTemp}`);

        const data = await res.json();

        console.log("API DATA:", data);
        console.log("OUTSIDE TEMP:", data.outside_temp);     

        // 🔥 FIX: force number
        state.outsideTemp = Number(data.outside_temp);

        if (data.heat !== undefined) {
            setHeatLevel(data.heat);
        }

        updateUI();

    } catch (err) {
        console.error("API Error:", err);
    }
}
async function fetchLiveTemp() {
    try {
        const res = await fetch("http://192.168.137.1:5002/latest");
        const data = await res.json();

        // ✅ ONLY THIS FUNCTION CONTROLS TEMP
        document.getElementById("shoe-temp").innerText = data.shoe_temp.toFixed(2);

    } catch (err) {
        console.error("Error:", err);
    }
}

/* ================= MOCK ================= */

// function startMockDeviceData() {
//     if (mockBleInterval) clearInterval(mockBleInterval);

//     mockBleInterval = setInterval(() => {
//         if (state.currentHeatLevel === 0) {
//             state.shoeTemp -= 0.1;
//         } else {
//             state.shoeTemp += (0.15 * state.currentHeatLevel);
//         }

//         if (state.shoeTemp < 10) state.shoeTemp = 10;

//         updateUI();
//     }, 2000);
// }

document.addEventListener('DOMContentLoaded', init);
setInterval(fetchLiveTemp, 2000);
setInterval(checkESP32Connection, 3000);