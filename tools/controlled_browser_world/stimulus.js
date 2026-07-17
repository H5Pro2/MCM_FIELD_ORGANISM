const canvas = document.querySelector("#world");
const context = canvas.getContext("2d", { alpha: false });
const startButton = document.querySelector("#start");
const statusNode = document.querySelector("#status");
const completeNode = document.querySelector("#complete");
const resultStatus = document.querySelector("#result-status");
const restartButton = document.querySelector("#restart");

let audioContext;
let oscillator;
let gainNode;
let program;
let animationFrame;

function resize() {
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.round(window.innerWidth * scale);
  canvas.height = Math.round(window.innerHeight * scale);
  context.setTransform(scale, 0, 0, scale, 0, 0);
}

function drawSquare(centerX) {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const size = Math.max(72, Math.min(width, height) * 0.18);
  context.fillStyle = "#202428";
  context.fillRect(0, 0, width, height);
  context.fillStyle = "#f5f7f8";
  context.fillRect(centerX - size / 2, height / 2 - size / 2, size, size);
}

function phaseAt(elapsedMs) {
  let cursor = 0;
  for (const phase of program.phases) {
    const end = cursor + phase.duration_ms;
    if (elapsedMs < end) {
      return { phase, localMs: Math.max(0, elapsedMs - cursor) };
    }
    cursor = end;
  }
  return null;
}

function render() {
  const elapsed = Date.now() - program.start_epoch_ms;
  const active = phaseAt(elapsed);
  const center = window.innerWidth / 2;
  if (!active || elapsed < 0) {
    drawSquare(center);
  } else if (active.phase.visual_mode === "moving") {
    const progress = active.localMs / active.phase.duration_ms;
    const angle = progress * Math.PI * 2 * program.movement_cycles;
    drawSquare(center + Math.sin(angle) * window.innerWidth * 0.30);
  } else {
    drawSquare(center);
  }
  animationFrame = requestAnimationFrame(render);
}

async function pollResult() {
  const response = await fetch("/api/status", { cache: "no-store" });
  const payload = await response.json();
  if (payload.status === "complete") {
    document.body.classList.remove("running");
    document.body.classList.add("complete");
    completeNode.hidden = false;
    resultStatus.textContent = "Kamera- und Mikrofonlauf wurden ohne Rohdatenspeicherung abgeschlossen.";
    return;
  }
  if (payload.status === "failed") {
    document.body.classList.remove("running");
    document.body.classList.add("complete");
    completeNode.hidden = false;
    resultStatus.textContent = payload.error || "Der Lauf ist fehlgeschlagen.";
    return;
  }
  window.setTimeout(pollResult, 500);
}

function scheduleTone() {
  const delaySeconds = Math.max(0, (program.start_epoch_ms - Date.now()) / 1000);
  let cursorSeconds = delaySeconds;
  oscillator.frequency.setValueAtTime(
    program.tone_frequency_hz,
    audioContext.currentTime,
  );
  gainNode.gain.setValueAtTime(0, audioContext.currentTime);
  for (const phase of program.phases) {
    gainNode.gain.setValueAtTime(
      phase.tone_gain,
      audioContext.currentTime + cursorSeconds,
    );
    cursorSeconds += phase.duration_ms / 1000;
  }
  gainNode.gain.setValueAtTime(0, audioContext.currentTime + cursorSeconds);
}

async function start() {
  startButton.disabled = true;
  statusNode.textContent = "Kamera wird vorbereitet.";
  audioContext = new AudioContext();
  await audioContext.resume();
  oscillator = audioContext.createOscillator();
  gainNode = audioContext.createGain();
  oscillator.connect(gainNode).connect(audioContext.destination);
  oscillator.start();
  document.documentElement.requestFullscreen?.().catch(() => {});

  try {
    const preparedResponse = await fetch("/api/prepare", { method: "POST" });
    const prepared = await preparedResponse.json();
    if (!preparedResponse.ok) {
      throw new Error(prepared.error || "Kamera konnte nicht vorbereitet werden.");
    }
    statusNode.textContent = `${prepared.startup_frames} Startframes abgeschlossen.`;

    const startResponse = await fetch("/api/start", { method: "POST" });
    program = await startResponse.json();
    if (!startResponse.ok) {
      throw new Error(program.error || "Lauf konnte nicht gestartet werden.");
    }
    scheduleTone();
    document.body.classList.add("running");
    animationFrame = requestAnimationFrame(render);
    const totalMs = program.phases.reduce(
      (total, phase) => total + phase.duration_ms,
      0,
    );
    window.setTimeout(pollResult, Math.max(0, program.start_epoch_ms - Date.now()) + totalMs);
  } catch (error) {
    oscillator?.stop();
    startButton.disabled = false;
    statusNode.textContent = error.message;
  }
}

window.addEventListener("resize", resize);
window.addEventListener("beforeunload", () => {
  cancelAnimationFrame(animationFrame);
  oscillator?.stop();
  audioContext?.close();
});
startButton.addEventListener("click", start);
restartButton.addEventListener("click", () => window.location.reload());
resize();
drawSquare(window.innerWidth / 2);
