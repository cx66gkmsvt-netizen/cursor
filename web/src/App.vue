<template>
  <div class="app">
    <h1>DeepSeek Chat</h1>
    <textarea
      v-model="prompt"
      rows="6"
      placeholder="输入内容"
      @keydown.ctrl.enter.prevent="send"
    ></textarea>
    <button :disabled="loading || !prompt.trim()" @click="send">
      {{ loading ? "发送中..." : "发送" }}
    </button>
    <div class="output" :class="{ loading }">
      <pre v-if="reply">{{ reply }}</pre>
      <span v-else-if="loading">等待回复...</span>
      <span v-else>输出将在这里显示</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p class="hint">提示：Ctrl+Enter 快捷发送</p>
  </div>
</template>

<script setup>
import { ref } from "vue";

const prompt = ref("");
const reply = ref("");
const loading = ref(false);
const error = ref("");

const send = async () => {
  if (!prompt.value.trim() || loading.value) return;
  error.value = "";
  reply.value = "";
  loading.value = true;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt.value }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    reply.value = data.reply || "";
  } catch (e) {
    error.value = e.message || "请求失败";
  } finally {
    loading.value = false;
  }
};
</script>

