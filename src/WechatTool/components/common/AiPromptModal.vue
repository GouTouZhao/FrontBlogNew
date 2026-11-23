<template>
  <a-modal
    v-model:open="innerOpen"
    title="AI提示词模板（快速生成可导入聊天文本）"
    width="820px"
    :footer="null"
    destroyOnClose
  >
    <div class="ai-prompt-modal">
      <!-- 1. 用户输入区：主题 / 大概描述 -->
      <div class="section-block">
        <div class="section-header">
          <span class="section-title">1. 输入对话主题 / 大概描述</span>
          <div class="section-controls">
            <a-radio-group v-model:value="mode" size="small" button-style="solid">
              <a-radio-button value="single">单张图</a-radio-button>
              <a-radio-button value="batch">多张分图 (---)</a-radio-button>
            </a-radio-group>
            <a-select v-model:value="modelLabel" size="small" style="width: 102px">
              <a-select-option value="华为细圆">华为细圆</a-select-option>
              <a-select-option value="默认机型">默认机型</a-select-option>
            </a-select>
            <a-input
              v-model:value="otherName"
              size="small"
              allow-clear
              placeholder="对方昵称（可选）"
              style="width: 136px"
            />
          </div>
        </div>
        <a-textarea
          v-model:value="topicInput"
          :rows="3"
          allow-clear
          placeholder="直接输入对话主题或大概剧情，下方会即时生成发给 AI 的完整提示词。例如：&#10;女朋友生理期肚子疼，我先温柔安慰她，再转了88元让她点热奶茶，她收款后发了一条5秒语音谢谢我。"
        />
      </div>

      <!-- 2. 文字标准化例子与说明 -->
      <div class="section-block">
        <div class="section-header">
          <span class="section-title">2. 文字标准化说明与例子（AI 将按此规范输出文本）</span>
          <a-button size="small" type="link" @click="showSpec = !showSpec">
            {{ showSpec ? "收起说明" : "展开说明" }}
          </a-button>
        </div>
        <div v-show="showSpec" class="spec-grid">
          <div class="spec-rules">
            <div class="sub-title">格式规则说明</div>
            <ul class="rule-list">
              <li v-for="item in STANDARD_FORMAT_ITEMS" :key="item.label">
                <strong>{{ item.label }}：</strong>
                <span>{{ item.syntax }}</span>
              </li>
            </ul>
          </div>
          <div class="spec-example">
            <div class="sub-title-row">
              <span class="sub-title">标准化文字例子（{{ mode === "batch" ? "多图批量" : "单图" }}）</span>
              <a-button size="small" type="link" @click="handleCopyExample">复制例子</a-button>
            </div>
            <pre class="example-code">{{ currentExample }}</pre>
          </div>
        </div>
      </div>

      <!-- 3. 即时生成的 AI 提示词 -->
      <div class="section-block">
        <div class="section-header">
          <span class="section-title">3. 即时生成的 AI 提示词（可直接复制发给 AI）</span>
          <div class="prompt-actions">
            <a-button size="small" @click="topicInput = ''">清空描述</a-button>
            <a-button type="primary" size="small" @click="handleCopyPrompt">
              复制AI提示词
            </a-button>
          </div>
        </div>
        <a-textarea
          :value="generatedPrompt"
          :rows="10"
          readonly
          class="prompt-output"
        />
        <div class="prompt-tip">
          使用步骤：点击「复制AI提示词」发给任意 AI → 复制 AI 返回的纯文本 → 粘贴到【导入聊天】或【批量生成】即可直接配置入图片。
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { toast } from "@/WechatTool/utils/feedback";
import {
  STANDARD_TEXT_EXAMPLE_SINGLE,
  STANDARD_TEXT_EXAMPLE_BATCH,
  STANDARD_FORMAT_ITEMS,
  buildAiChatPrompt,
  copyWithClipboardFallback,
} from "@/WechatTool/utils/aiPromptHelper";

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  defaultMode: {
    type: String,
    default: "single",
  },
  defaultModel: {
    type: String,
    default: "华为细圆",
  },
});

const emit = defineEmits(["update:open"]);

const innerOpen = computed({
  get: () => props.open,
  set: (val) => emit("update:open", val),
});

const topicInput = ref("");
const otherName = ref("");
const mode = ref(props.defaultMode === "batch" ? "batch" : "single");
const modelLabel = ref(props.defaultModel || "华为细圆");
const showSpec = ref(true);

watch(
  () => props.open,
  (val) => {
    if (val) {
      mode.value = props.defaultMode === "batch" ? "batch" : "single";
      if (props.defaultModel) {
        modelLabel.value = props.defaultModel;
      }
    }
  }
);

const currentExample = computed(() =>
  mode.value === "batch" ? STANDARD_TEXT_EXAMPLE_BATCH : STANDARD_TEXT_EXAMPLE_SINGLE
);

const generatedPrompt = computed(() =>
  buildAiChatPrompt({
    topic: topicInput.value,
    mode: mode.value,
    modelLabel: modelLabel.value,
    otherName: otherName.value,
  })
);

const handleCopyPrompt = async () => {
  await copyWithClipboardFallback(generatedPrompt.value);
  toast({
    type: "success",
    content: "AI提示词已复制，直接粘贴给 AI 生成后即可导入使用",
  });
};

const handleCopyExample = async () => {
  await copyWithClipboardFallback(currentExample.value);
  toast({
    type: "success",
    content: "标准化文字示例已复制到剪贴板",
  });
};
</script>

<style lang="less" scoped>
.ai-prompt-modal {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 75vh;
  overflow-y: auto;
  padding-right: 4px;

  .section-block {
    background: #fafafa;
    border: 1px solid #ececec;
    border-radius: 8px;
    padding: 12px 14px;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }

  .section-title {
    font-size: 13px;
    font-weight: 600;
    color: #222;
  }

  .section-controls,
  .prompt-actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .spec-grid {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 12px;

    @media (max-width: 720px) {
      grid-template-columns: 1fr;
    }
  }

  .spec-rules,
  .spec-example {
    background: #fff;
    border: 1px solid #eee;
    border-radius: 6px;
    padding: 10px 12px;
  }

  .sub-title {
    font-size: 12px;
    font-weight: 600;
    color: #444;
    margin-bottom: 6px;
  }

  .sub-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;

    .sub-title {
      margin-bottom: 0;
    }
  }

  .rule-list {
    margin: 0;
    padding-left: 16px;
    font-size: 12px;
    line-height: 1.55;
    color: #555;

    li + li {
      margin-top: 3px;
    }

    strong {
      color: #222;
    }
  }

  .example-code {
    margin: 0;
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 12px;
    line-height: 1.5;
    color: #333;
    background: #f6f8fa;
    border-radius: 4px;
    padding: 8px 10px;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 210px;
    overflow-y: auto;
  }

  .prompt-output {
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 12px;
    line-height: 1.55;
    background: #fff;
  }

  .prompt-tip {
    margin-top: 6px;
    font-size: 12px;
    color: #888;
  }
}
</style>

