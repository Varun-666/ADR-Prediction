// ============================================================
// ADR Prediction — Rate Desk frontend logic
// ============================================================

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const ROOM_TYPES = ["A", "B", "C", "D", "E", "F", "G", "H", "L", "P"];

const MEALS = [
  { value: "BB", label: "BB — Bed & Breakfast" },
  { value: "HB", label: "HB — Half Board" },
  { value: "FB", label: "FB — Full Board" },
  { value: "SC", label: "SC — Self Catering" },
  { value: "Undefined", label: "Undefined" },
];

const MARKET_SEGMENTS = [
  "Direct", "Corporate", "Online TA", "Offline TA/TO",
  "Complementary", "Groups", "Aviation", "Undefined",
];

const DISTRIBUTION_CHANNELS = ["Direct", "Corporate", "TA/TO", "GDS", "Undefined"];

const DEPOSIT_TYPES = ["No Deposit", "Refundable", "Non Refund"];

const CUSTOMER_TYPES = ["Transient", "Transient-Party", "Contract", "Group"];

// Full ISO 3166-1 alpha-3 list the model was trained on.
const COUNTRIES = ["ABW","AGO","AIA","ALB","AND","ARE","ARG","ARM","ASM","ATA","ATF","AUS","AUT","AZE","BDI","BEL","BEN","BFA","BGD","BGR","BHR","BHS","BIH","BLR","BOL","BRA","BRB","BWA","CAF","CHE","CHL","CHN","CIV","CMR","CN","COL","COM","CPV","CRI","CUB","CYP","CZE","DEU","DMA","DNK","DOM","DZA","ECU","EGY","ESP","EST","ETH","FIN","FJI","FRA","FRO","GAB","GBR","GEO","GGY","GHA","GIB","GLP","GNB","GRC","GTM","GUY","HKG","HND","HRV","HUN","IDN","IMN","IND","IRL","IRN","IRQ","ISL","ISR","ITA","JAM","JEY","JOR","JPN","KAZ","KEN","KHM","KIR","KNA","KOR","KWT","LAO","LBN","LBY","LCA","LIE","LKA","LTU","LUX","LVA","MAC","MAR","MCO","MDG","MDV","MEX","MKD","MLI","MLT","MMR","MNE","MOZ","MRT","MUS","MWI","MYS","MYT","NAM","NCL","NGA","NIC","NLD","NOR","NZL","OMN","PAK","PAN","PER","PHL","POL","PRI","PRT","PRY","PYF","QAT","ROU","RUS","RWA","SAU","SEN","SGP","SLE","SLV","SMR","SRB","STP","SUR","SVK","SVN","SWE","SYC","SYR","TGO","THA","TJK","TMP","TUN","TUR","TWN","TZA","UGA","UKR","UMI","URY","USA","UZB","Unknown","VEN","VGB","VNM","ZAF","ZMB","ZWE"];

function fillSelect(select, options, { defaultValue } = {}) {
  select.innerHTML = "";
  for (const opt of options) {
    const value = typeof opt === "string" ? opt : opt.value;
    const label = typeof opt === "string" ? opt : opt.label;
    const el = document.createElement("option");
    el.value = value;
    el.textContent = label;
    select.appendChild(el);
  }
  if (defaultValue) select.value = defaultValue;
}

function populateDropdowns() {
  const form = document.getElementById("booking-form");
  fillSelect(form.arrival_date_month, MONTHS, { defaultValue: "July" });
  fillSelect(form.reserved_room_type, ROOM_TYPES, { defaultValue: "A" });
  fillSelect(form.meal, MEALS, { defaultValue: "BB" });
  fillSelect(form.market_segment, MARKET_SEGMENTS, { defaultValue: "Online TA" });
  fillSelect(form.distribution_channel, DISTRIBUTION_CHANNELS, { defaultValue: "TA/TO" });
  fillSelect(form.deposit_type, DEPOSIT_TYPES, { defaultValue: "No Deposit" });
  fillSelect(form.customer_type, CUSTOMER_TYPES, { defaultValue: "Transient" });
  fillSelect(form.country, COUNTRIES, { defaultValue: "USA" });
}

function animateValue(el, from, to, duration = 700) {
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = from + (to - from) * eased;
    el.textContent = current.toFixed(2);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function readFormAsPayload(form) {
  const fd = new FormData(form);
  const payload = {};
  for (const [key, value] of fd.entries()) {
    const numericFields = new Set([
      "lead_time", "arrival_date_year", "arrival_date_week_number",
      "arrival_date_day_of_month", "stays_in_weekend_nights",
      "stays_in_week_nights", "adults", "children", "babies",
      "is_repeated_guest", "previous_cancellations",
      "previous_bookings_not_canceled", "booking_changes",
      "days_in_waiting_list", "required_car_parking_spaces",
      "total_of_special_requests",
    ]);
    payload[key] = numericFields.has(key) ? Number(value) : value;
  }
  return payload;
}

function renderSummary(payload, engineered) {
  const box = document.getElementById("summary-box");
  const list = document.getElementById("summary-list");
  list.innerHTML = "";

  const rows = [
    ["Hotel", payload.hotel],
    ["Arrival", `${payload.arrival_date_month} ${payload.arrival_date_day_of_month}, ${payload.arrival_date_year}`],
    ["Room type", payload.reserved_room_type],
    ["Lead time", `${payload.lead_time} days`],
    ["Guests", `${payload.adults} adults, ${payload.children} children, ${payload.babies} babies`],
    ["Nights", `${payload.stays_in_weekend_nights} weekend, ${payload.stays_in_week_nights} week`],
    ["Market segment", payload.market_segment],
  ];

  for (const [label, value] of rows) {
    const li = document.createElement("li");
    li.innerHTML = `<span>${label}:</span> <strong>${value}</strong>`;
    list.appendChild(li);
  }
  box.hidden = false;
}

async function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const btn = document.getElementById("predict-btn");
  const note = document.getElementById("quote-note");
  const adrValueEl = document.getElementById("adr-value");

  const payload = readFormAsPayload(form);

  btn.disabled = true;
  btn.querySelector("span").textContent = "Quoting…";
  note.classList.remove("error");
  note.textContent = "Running the booking details through the trained model…";

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }

    const data = await res.json();

    const previous = parseFloat(adrValueEl.textContent) || 0;
    animateValue(adrValueEl, previous, data.predicted_adr);

    document.getElementById("meta-season").textContent = data.season;
    document.getElementById("meta-guests").textContent = data.total_guests;
    document.getElementById("meta-nights").textContent = data.total_nights;

    renderSummary(payload, data);

    note.textContent = "Quote generated from the live Random Forest model. Adjust any field and quote again to compare rates.";
  } catch (err) {
    note.classList.add("error");
    note.textContent = `Couldn't generate a quote: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.querySelector("span").textContent = "Quote this rate";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  populateDropdowns();
  document.getElementById("booking-form").addEventListener("submit", handleSubmit);
});
