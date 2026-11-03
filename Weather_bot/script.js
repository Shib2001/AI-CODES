const form = document.querySelector("#weather-form");
const cityInput = document.querySelector("#city-input");
const searchButton = document.querySelector("#search-button");
const listenButton = document.querySelector("#listen-button");
const statusMessage = document.querySelector("#status-message");
const weatherPanel = document.querySelector("#weather-panel");
const locationName = document.querySelector("#location-name");
const localTime = document.querySelector("#local-time");
const weatherIcon = document.querySelector("#weather-icon");
const currentTemperature = document.querySelector("#current-temperature");
const currentCondition = document.querySelector("#current-condition");
const weatherReport = document.querySelector("#weather-report");
const weatherDetails = document.querySelector("#weather-details");
const speakButton = document.querySelector("#speak-button");

let latestReport = "";
let recognition = null;
let reportAudio = null;
let reportAudioUrl = null;

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = navigator.language || "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    listenButton.disabled = true;
    listenButton.classList.add("listening");
    showStatus("Listening… say a city name.", "loading");
  };

  recognition.onresult = (event) => {
    const city = event.results[0][0].transcript.trim();
    if (!city) {
      showStatus("I didn’t catch a city name. Please try again.", "error");
      return;
    }

    cityInput.value = city;
    showStatus(`I heard “${city}”. Checking the weather…`, "loading");
    form.requestSubmit();
  };

  recognition.onerror = (event) => {
    const messages = {
      "not-allowed": "Microphone access is blocked. Allow it in your browser settings.",
      "service-not-allowed": "Speech recognition is unavailable in this browser.",
      "no-speech": "I didn’t hear anything. Please try speaking again.",
      network: "Speech recognition needs an internet connection.",
    };
    if (event.error !== "aborted") {
      showStatus(messages[event.error] || "Speech recognition failed. Please try again.", "error");
    }
  };

  recognition.onend = () => {
    listenButton.disabled = false;
    listenButton.classList.remove("listening");
  };
} else {
  listenButton.disabled = true;
  listenButton.title = "Speech input is not supported in this browser";
  listenButton.setAttribute("aria-label", "Speech input is not supported in this browser");
}

function showStatus(message, state = "") {
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${state}`.trim();
}

function formatTemperature(value) {
  return value == null ? "—" : `${Math.round(value)}°`;
}

function addDetail(label, value) {
  const item = document.createElement("div");
  item.className = "detail-item";

  const title = document.createElement("p");
  title.className = "detail-label";
  title.textContent = label;

  const reading = document.createElement("p");
  reading.className = "detail-value";
  reading.textContent = value;

  item.append(title, reading);
  weatherDetails.append(item);
}

function iconForCondition(condition) {
  if (/thunder|storm/i.test(condition)) return "ϟ";
  if (/snow|sleet/i.test(condition)) return "❄";
  if (/rain|drizzle|shower/i.test(condition)) return "☂";
  if (/fog/i.test(condition)) return "≋";
  if (/cloud|overcast/i.test(condition)) return "☁";
  return "☀";
}

function renderWeather(weather, report) {
  if (reportAudio) {
    reportAudio.pause();
    reportAudio = null;
  }
  if (reportAudioUrl) {
    URL.revokeObjectURL(reportAudioUrl);
    reportAudioUrl = null;
  }

  locationName.textContent = weather.location;
  localTime.textContent = weather.local_time
    ? `${weather.period === "tomorrow" ? "Forecast" : "Local time"} · ${weather.period_date || weather.local_time.replace("T", " ")}`
    : "Current local conditions";
  weatherIcon.textContent = iconForCondition(weather.condition);
  currentTemperature.textContent = formatTemperature(weather.temperature_c);
  currentCondition.textContent = weather.condition;
  weatherReport.textContent = report;
  latestReport = report;

  weatherDetails.replaceChildren();
  const periodLabel = weather.period === "tomorrow" ? "Tomorrow" : "Today";
  document.querySelector(".details-heading h2").textContent = `${periodLabel}, at a glance`;
  addDetail("Feels like", formatTemperature(weather.feels_like_c));
  addDetail(`${periodLabel}’s high`, formatTemperature(weather.today_high_c));
  addDetail(`${periodLabel}’s low`, formatTemperature(weather.today_low_c));
  addDetail(
    "Wind",
    weather.wind_kmh == null ? "—" : `${Math.round(weather.wind_kmh)} km/h`,
  );
  addDetail(
    "Humidity",
    weather.humidity_percent == null ? "—" : `${weather.humidity_percent}%`,
  );
  addDetail(
    "Precipitation",
    weather.precipitation_mm == null ? "—" : `${weather.precipitation_mm} mm`,
  );
  addDetail(
    "Rain chance",
    weather.precipitation_probability_percent == null
      ? "—"
      : `${weather.precipitation_probability_percent}%`,
  );
  if (weather.rainy_season) {
    addDetail(
      "Typical wet season",
      weather.rainy_season.is_typically_wet_month ? "Usually yes" : "Usually no",
    );
  }

  weatherPanel.hidden = false;
  speakButton.disabled = false;
}

listenButton.addEventListener("click", () => {
  if (!recognition) return;
  try {
    recognition.start();
  } catch (error) {
    const message = error.name === "InvalidStateError"
      ? "Speech recognition is already listening."
      : "Could not start speech recognition. Please try again.";
    showStatus(message, error.name === "InvalidStateError" ? "loading" : "error");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const city = cityInput.value.trim();
  if (!city) {
    cityInput.focus();
    return;
  }

  searchButton.disabled = true;
  searchButton.querySelector("span").textContent = "Checking…";
  weatherPanel.hidden = true;
  showStatus("Finding the latest conditions…", "loading");

  try {
    const response = await fetch("/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: city }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || data.error || "Could not load weather. Please try again.");
    }

    renderWeather(data.weather, data.report);
    showStatus("Here’s a little clarity for your day.");
  } catch (error) {
    showStatus(error.message || "Something went wrong. Please try again.", "error");
  } finally {
    searchButton.disabled = false;
    searchButton.querySelector("span").textContent = "Find weather";
  }
});

speakButton.addEventListener("click", async () => {
  if (!latestReport) {
    showStatus("There is no weather report to read aloud yet.", "error");
    return;
  }

  speakButton.disabled = true;
  speakButton.querySelector("span").textContent = "Preparing voice…";
  showStatus("Preparing your gentle weather report…", "loading");

  try {
    const response = await fetch("/api/speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: latestReport }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Could not create speech. Please try again.");
    }

    if (reportAudio) {
      reportAudio.pause();
      URL.revokeObjectURL(reportAudioUrl);
    }
    reportAudioUrl = URL.createObjectURL(await response.blob());
    reportAudio = new Audio(reportAudioUrl);
    reportAudio.addEventListener("ended", () => {
      URL.revokeObjectURL(reportAudioUrl);
      reportAudioUrl = null;
      reportAudio = null;
      speakButton.disabled = false;
      speakButton.querySelector("span").textContent = "Listen to report";
    }, { once: true });
    await reportAudio.play();
    speakButton.querySelector("span").textContent = "Speaking…";
    showStatus("Playing your weather report.", "loading");
  } catch (error) {
    showStatus(error.message || "Could not play the weather report.", "error");
    speakButton.disabled = false;
    speakButton.querySelector("span").textContent = "Listen to report";
    if (reportAudioUrl) {
      URL.revokeObjectURL(reportAudioUrl);
      reportAudioUrl = null;
    }
    reportAudio = null;
  }
});
