<script setup>
import { ref, onBeforeUnmount, nextTick } from "vue";
import Icon from "./AppIcon.vue";
const video = ref(null),
  active = ref(false),
  ready = ref(false),
  error = ref("");
let stream,
  disposed = false;
async function start() {
  error.value = "";
  try {
    if (!navigator.mediaDevices?.getUserMedia)
      throw Error("Camera needs HTTPS or localhost and a supported browser.");
    const acquired = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false,
    });
    if (disposed) {
      acquired.getTracks().forEach((t) => t.stop());
      return;
    }
    stream = acquired;
    active.value = true;
    await nextTick();
    video.value.srcObject = stream;
    await video.value.play();
  } catch (e) {
    error.value =
      e.name === "NotAllowedError"
        ? "Camera permission was denied. Allow camera access and try again."
        : e.message;
    stop();
  }
}
function stop() {
  stream?.getTracks().forEach((t) => t.stop());
  stream = null;
  active.value = false;
  ready.value = false;
}
function capture() {
  if (!ready.value || !video.value?.videoWidth)
    throw Error("Start the camera and wait for the preview.");
  const canvas = document.createElement("canvas");
  canvas.width = 640;
  canvas.height = 480;
  canvas.getContext("2d").drawImage(video.value, 0, 0, 640, 480);
  return canvas.toDataURL("image/jpeg", 0.75);
}
async function burst() {
  const frames = [];
  for (let i = 0; i < 14; i++) {
    if (disposed) throw Error("Capture cancelled.");
    frames.push(capture());
    await new Promise((r) => setTimeout(r, 200));
  }
  return frames;
}
defineExpose({ capture, burst, stop, ready });
onBeforeUnmount(() => {
  disposed = true;
  stop();
});
</script>
<template>
  <div>
    <div class="camera">
      <video
        v-if="active"
        ref="video"
        autoplay
        muted
        playsinline
        @loadeddata="ready = true"
        aria-label="Live camera preview"
      ></video>
      <div v-else class="camera-placeholder">
        <Icon name="camera" />
        <h3>Your camera, your control</h3>
        <p>
          Your camera starts only when you choose.<br />Keep your face centred
          in good lighting.
        </p>
        <button type="button" class="button" @click="start">
          Enable camera
        </button>
      </div>
    </div>
    <div v-if="error" class="notice error" role="alert">{{ error }}</div>
    <button v-if="active" type="button" class="button ghost mt" @click="stop">
      Turn camera off
    </button>
  </div>
</template>
