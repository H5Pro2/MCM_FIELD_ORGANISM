"use strict";

const canvas = document.querySelector("#world");
const context = canvas.getContext("2d", { alpha: false });
let worldContract = null;
let sourceConfig = null;
let renderedAudio = null;

function requireConfigured() {
  if (worldContract === null || sourceConfig === null) {
    throw new Error("controlled AV world is not configured");
  }
}

function requireInteger(value, role, minimum = 1) {
  if (!Number.isInteger(value) || value < minimum) {
    throw new Error(`${role} must be an integer of at least ${minimum}`);
  }
}

function requireFinite(value, role) {
  if (!Number.isFinite(value)) {
    throw new Error(`${role} must be finite`);
  }
}

function configureWorld(worldPayload, sourcePayload) {
  if (worldContract !== null || sourceConfig !== null) {
    throw new Error("controlled AV world can be configured only once");
  }
  if (!worldPayload || !sourcePayload || !Array.isArray(worldPayload.phases)) {
    throw new Error("controlled AV world requires two complete contracts");
  }
  requireInteger(sourcePayload.canvas_width, "canvas_width");
  requireInteger(sourcePayload.canvas_height, "canvas_height");
  requireInteger(sourcePayload.audio_sample_rate, "audio_sample_rate");
  requireInteger(sourcePayload.audio_hop_size, "audio_hop_size");
  requireFinite(sourcePayload.visual_frames_per_second, "visual_frames_per_second");
  requireFinite(sourcePayload.motion_amplitude_fraction, "motion_amplitude_fraction");
  requireFinite(sourcePayload.foreground_size_fraction, "foreground_size_fraction");
  if (sourcePayload.device_scale_factor !== 1) {
    throw new Error("device_scale_factor must be one");
  }
  if (!["horizontal", "vertical"].includes(sourcePayload.motion_axis)) {
    throw new Error("motion_axis is invalid");
  }
  if (sourcePayload.audio_channel_count !== 1 || sourcePayload.oscillator_type !== "sine") {
    throw new Error("audio source contract is invalid");
  }
  canvas.width = sourcePayload.canvas_width;
  canvas.height = sourcePayload.canvas_height;
  worldContract = Object.freeze(worldPayload);
  sourceConfig = Object.freeze(sourcePayload);
  renderedAudio = null;
}

function phaseAt(tickNs) {
  let cursor = 0;
  for (const phase of worldContract.phases) {
    const end = cursor + phase.duration_ns;
    if (tickNs < end) {
      return { phase, startNs: cursor };
    }
    cursor = end;
  }
  return null;
}

function rgb(values) {
  return `rgb(${values[0]}, ${values[1]}, ${values[2]})`;
}

function renderVisualFrame(frameIndex) {
  requireConfigured();
  requireInteger(frameIndex, "frameIndex", 0);
  const tickNs = Math.floor(
    frameIndex * 1000000000 / sourceConfig.visual_frames_per_second,
  );
  const active = phaseAt(tickNs);
  if (active === null) {
    throw new Error("visual frame is outside the world horizon");
  }

  const width = sourceConfig.canvas_width;
  const height = sourceConfig.canvas_height;
  const extent = Math.min(width, height);
  const size = extent * sourceConfig.foreground_size_fraction;
  let offset = 0;
  if (active.phase.visual_mode === "moving") {
    const local = (tickNs - active.startNs) / active.phase.duration_ns;
    offset = (
      extent
      * sourceConfig.motion_amplitude_fraction
      * Math.sin(2 * Math.PI * worldContract.movement_cycles * local)
    );
  }
  const centerX = width / 2 + (sourceConfig.motion_axis === "horizontal" ? offset : 0);
  const centerY = height / 2 + (sourceConfig.motion_axis === "vertical" ? offset : 0);
  context.fillStyle = rgb(sourceConfig.background_rgb);
  context.fillRect(0, 0, width, height);
  context.fillStyle = rgb(sourceConfig.foreground_rgb);
  context.fillRect(centerX - size / 2, centerY - size / 2, size, size);
}

function phaseSampleCounts() {
  return worldContract.phases.map((phase) => {
    const count = phase.duration_ns * sourceConfig.audio_sample_rate / 1000000000;
    requireInteger(count, "phase audio sample count");
    return count;
  });
}

async function renderAudio() {
  requireConfigured();
  if (renderedAudio !== null) {
    throw new Error("audio is already rendered");
  }
  const counts = phaseSampleCounts();
  const sampleCount = counts.reduce((total, count) => total + count, 0);
  const activeIndices = worldContract.phases
    .map((phase, index) => phase.tone_gain > 0 ? index : -1)
    .filter((index) => index >= 0);
  if (activeIndices.length !== 1) {
    throw new Error("canonical audio requires exactly one active phase");
  }
  const activeIndex = activeIndices[0];
  const activeGain = worldContract.phases[activeIndex].tone_gain;
  const activeStart = counts
    .slice(0, activeIndex)
    .reduce((total, count) => total + count, 0);
  const activeCount = counts[activeIndex];

  const offline = new OfflineAudioContext(1, sampleCount, sourceConfig.audio_sample_rate);
  const buffer = offline.createBuffer(1, sampleCount, sourceConfig.audio_sample_rate);
  const samples = buffer.getChannelData(0);
  for (let localIndex = 0; localIndex < activeCount; localIndex += 1) {
    samples[activeStart + localIndex] = (
      activeGain
      * Math.sin(
        2 * Math.PI * worldContract.tone_frequency_hz * localIndex
        / sourceConfig.audio_sample_rate
      )
    );
  }
  const source = offline.createBufferSource();
  source.buffer = buffer;
  source.connect(offline.destination);
  source.start(0);
  source.stop(sampleCount / sourceConfig.audio_sample_rate);
  renderedAudio = (await offline.startRendering()).getChannelData(0);
  if (renderedAudio.length !== sampleCount) {
    renderedAudio = null;
    throw new Error("canonical audio sample inventory changed");
  }
  return renderedAudio.length;
}

function readAudioChunk(chunkIndex) {
  requireConfigured();
  if (renderedAudio === null) {
    throw new Error("audio must be rendered before reading chunks");
  }
  requireInteger(chunkIndex, "chunkIndex", 0);
  const start = chunkIndex * sourceConfig.audio_hop_size;
  const end = start + sourceConfig.audio_hop_size;
  if (end > renderedAudio.length) {
    throw new Error("audio chunk is outside the rendered inventory");
  }
  return Array.from(renderedAudio.subarray(start, end));
}

function releaseAudio() {
  renderedAudio = null;
}

Object.assign(window, {
  configureWorld,
  readAudioChunk,
  releaseAudio,
  renderAudio,
  renderVisualFrame,
});
