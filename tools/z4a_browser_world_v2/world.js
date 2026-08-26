"use strict";

const WORLD_SPECS = Object.freeze({
  "z4a.browser.direct.reference.v2": Object.freeze({
    axis: "horizontal",
    frequencyHz: 660,
  }),
  "z4a.browser.direct.independent.v2": Object.freeze({
    axis: "vertical",
    frequencyHz: 990,
  }),
});

const SAMPLE_RATE = 48000;
const DURATION_SAMPLES = 1680000;
const canvas = document.querySelector("#world");
const context = canvas.getContext("2d", { alpha: false });
let selectedSpec = null;
let renderedAudio = null;

function requireSpec() {
  if (selectedSpec === null) {
    throw new Error("world must be configured before rendering");
  }
  return selectedSpec;
}

function configureWorld(worldId) {
  const spec = WORLD_SPECS[worldId];
  if (!spec) {
    throw new Error("unknown Z4-A browser world");
  }
  selectedSpec = spec;
  renderedAudio = null;
}

function renderVisualAt(tickNs) {
  const spec = requireSpec();
  if (!Number.isInteger(tickNs) || tickNs < 0 || tickNs >= 35000000000) {
    throw new Error("visual tick is outside the bound horizon");
  }
  let offset = 0;
  if (tickNs >= 7000000000 && tickNs < 14000000000) {
    const localSeconds = (tickNs - 7000000000) / 1000000000;
    offset = 144 * Math.sin(2 * Math.PI * 3 * localSeconds / 7);
  }
  const centerX = 240 + (spec.axis === "horizontal" ? offset : 0);
  const centerY = 240 + (spec.axis === "vertical" ? offset : 0);
  context.fillStyle = "rgb(32, 36, 40)";
  context.fillRect(0, 0, 480, 480);
  context.fillStyle = "rgb(245, 247, 248)";
  context.fillRect(centerX - 43.2, centerY - 43.2, 86.4, 86.4);
}

async function renderAudio() {
  const spec = requireSpec();
  const offline = new OfflineAudioContext(1, DURATION_SAMPLES, SAMPLE_RATE);
  const oscillator = offline.createOscillator();
  const gain = offline.createGain();
  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(spec.frequencyHz, 0);
  gain.gain.setValueAtTime(0, 0);
  gain.gain.setValueAtTime(0.18, 7);
  gain.gain.setValueAtTime(0, 14);
  gain.gain.setValueAtTime(0, 35);
  oscillator.connect(gain).connect(offline.destination);
  oscillator.start(0);
  oscillator.stop(35);
  renderedAudio = (await offline.startRendering()).getChannelData(0);
  if (renderedAudio.length !== DURATION_SAMPLES) {
    throw new Error("offline audio length changed");
  }
  return renderedAudio.length;
}

function readAudioChunk(chunkIndex) {
  if (renderedAudio === null) {
    throw new Error("audio must be rendered before reading chunks");
  }
  if (!Number.isInteger(chunkIndex) || chunkIndex < 0 || chunkIndex >= 3500) {
    throw new Error("audio chunk index is outside the bound inventory");
  }
  const start = chunkIndex * 480;
  return Array.from(renderedAudio.subarray(start, start + 480));
}

function releaseAudio() {
  renderedAudio = null;
}

Object.assign(window, {
  configureWorld,
  readAudioChunk,
  releaseAudio,
  renderAudio,
  renderVisualAt,
});
