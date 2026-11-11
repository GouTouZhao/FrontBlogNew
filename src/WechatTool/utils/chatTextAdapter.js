import { ownAvatar, otherAvatar } from "./avatar";
import { models } from "./enum";
import useStore from "@/WechatTool/store";

/**
 * 将聊天列表导出为简洁直观、适合人类阅读且能被系统重新解析的纯文本格式
 * 头像不作存储，按中文消息类型与角色进行适配
 * 
 * 格式示例：
 * 机型：华为细圆
 * 手机时间：17:30
 * 手机电量：76%
 * 对方用户名：派大星
 * 
 * 文本：我：你好派大星。
 * 文本：对方：你好GouTou！
 * 语音：对方：5秒
 * 通话：我：通话时长 00:10
 * 转账：我：88.00元：生日快乐
 * 红包：对方：恭喜发财，大吉大利
 * 撤回：我
 * 时间：昨天 上午16:48
 * 拍一拍：你 拍了拍 "派大星" 的脑门
 * 系统：消息已发出，但被对方拒收了。
 */
export function chatListToText(chatList = [], options = {}) {
  let systemStore = options?.systemStore;
  let userStore = options?.userStore;
  if (!systemStore || !userStore) {
    try {
      const store = useStore();
      if (!systemStore) systemStore = store.useSystemStore;
      if (!userStore) userStore = store.useUserStore;
    } catch (e) {}
  }

  // 1. 生成顶部机型与系统描述（机型、手机时间、电量、对方用户名）
  const modelVal = systemStore?.appearance?.model || "huawei_junxiu";
  const modelObj = models.find((m) => m.value === modelVal);
  const modelLabel = modelObj ? modelObj.label : (modelVal === "huawei_junxiu" ? "华为细圆" : "默认机型");

  const hour = String(systemStore?.appearance?.phoneTimeHour ?? "12").padStart(2, "0");
  const minute = String(systemStore?.appearance?.phoneTimeMinute ?? "00").padStart(2, "0");
  const phoneTime = `${hour}:${minute}`;

  const battery = `${systemStore?.appearance?.phoneBattery ?? 100}%`;

  const otherUser = userStore?.userList?.find((u) => u.role === "other") || (userStore?.userList?.length > 1 ? userStore.userList[1] : null);
  const otherNickname = otherUser?.nickname || systemStore?.appearance?.chatTitle || "派大星";

  const headerLines = [
    `机型：${modelLabel}`,
    `手机时间：${phoneTime}`,
    `手机电量：${battery}`,
    `对方用户名：${otherNickname}`,
    "",
  ];

  if (!Array.isArray(chatList) || !chatList.length) {
    return headerLines.join("\n");
  }

  const msgLines = chatList.map((chat) => {
    const isOwn = chat.role === "own";
    // 通用角色名称：我 vs 对方（不再输出易变的具体昵称）
    const sender = isOwn ? "我" : "对方";

    switch (chat.type) {
      case "text": {
        const typeLabel = chat.rejected ? "文本(拒收)" : "文本";
        const content = (chat.content || "").replace(/\r?\n/g, "\\n");
        return `${typeLabel}：${sender}：${content}`;
      }

      case "voice": {
        const duration = chat.duration || 1;
        if (chat.content) {
          return `语音：${sender}：${duration}秒：${chat.content}`;
        }
        return `语音：${sender}：${duration}秒`;
      }

      case "avInvite": {
        const isVideo = chat.invateType === "video";
        const typeLabel = isVideo ? "视频通话" : "通话";
        if (chat.state === "cancel") {
          return `${typeLabel}：${sender}：已取消`;
        }
        if (chat.state === "rejected") {
          return `${typeLabel}：${sender}：已拒绝`;
        }
        if (chat.state === "busy") {
          return `${typeLabel}：${sender}：忙线未接听`;
        }
        if (chat.state === "notConnect") {
          return `${typeLabel}：${sender}：未接听`;
        }
        const dur = chat.duration || "00:10";
        return `${typeLabel}：${sender}：通话时长 ${dur}`;
      }

      case "transferAccounts": {
        const money = Number(chat.money || 0).toFixed(2);
        if (chat.content) {
          return `转账：${sender}：${money}元：${chat.content}`;
        }
        return `转账：${sender}：${money}元`;
      }

      case "redEnvelope": {
        const content = chat.content || "恭喜发财，大吉大利";
        return `红包：${sender}：${content}`;
      }

      case "receive": {
        if (chat.receivedChatType === "redEnvelope") {
          return `红包领取：${sender}：领取了红包`;
        }
        return `转账收款：${sender}：已收款`;
      }

      case "image": {
        if (chat.content && (chat.content.startsWith("http://") || chat.content.startsWith("https://"))) {
          return `图片：${sender}：${chat.content}`;
        }
        return `图片：${sender}：[图片]`;
      }

      case "businessCard": {
        return `名片：${sender}：${chat.content || "个人名片"}`;
      }

      case "time": {
        return `时间：${chat.content || ""}`;
      }

      case "takeAPat": {
        return `拍一拍：${chat.content || ""}`;
      }

      case "revoke": {
        return `撤回：${sender}`;
      }

      case "system": {
        return `系统：${chat.content || ""}`;
      }

      default:
        return `文本：${sender}：${chat.content || ""}`;
    }
  });

  return [...headerLines, ...msgLines].join("\n");
}

/**
 * 将导出的文本解析回 chatList 数组，直接写入预览
 * 同时兼容旧版 JSON 字符串/对象格式，并解析顶部机型、时间、电量、对方用户名
 */
export function textToChatList(text, storeOrUserStore) {
  if (!text) return [];

  const trimmed = String(text).trim();

  // 1. 兼容旧版 JSON 格式
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) return parsed;
      if (parsed && Array.isArray(parsed.chatList)) return parsed.chatList;
    } catch (e) {
      // 非 JSON 则继续作为文本解析
    }
  }

  let userStore = null;
  let systemStore = null;

  if (storeOrUserStore) {
    if (storeOrUserStore.useUserStore || storeOrUserStore.userStore) {
      userStore = storeOrUserStore.userStore || storeOrUserStore.useUserStore;
      systemStore = storeOrUserStore.systemStore || storeOrUserStore.useSystemStore;
    } else if (storeOrUserStore.userList) {
      userStore = storeOrUserStore;
    }
  }

  if (!userStore || !systemStore) {
    try {
      const store = useStore();
      if (!userStore) userStore = store.useUserStore;
      if (!systemStore) systemStore = store.useSystemStore;
    } catch (e) {}
  }

  // 2. 解析文本行
  const rawLines = trimmed.split(/\r?\n/);
  const result = [];
  const baseTimestamp = Date.now();

  const userList = userStore?.userList || [];
  const ownUser = userList[0] || { id: "user-0", nickname: "你自己", role: "own", avatar: ownAvatar };
  const others = userList.slice(1);
  let defaultOther = others[0] || { id: "user-other", nickname: "派大星", role: "other", avatar: otherAvatar };

  // 辅助函数：根据发送者名称匹配用户与角色
  const matchUserAndRole = (senderName) => {
    const s = (senderName || "").trim();
    if (!s || s === "我" || s === "自己" || s === ownUser.nickname) {
      return {
        role: "own",
        user: ownUser,
      };
    }

    // 匹配其他用户（"对方" 或历史导出中特定的昵称）
    const found = others.find((u) => u.nickname === s);
    if (found) {
      return {
        role: "other",
        user: found,
      };
    }

    return {
      role: "other",
      user: defaultOther,
    };
  };

  rawLines.forEach((rawLine, idx) => {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || line.startsWith("//")) return;

    // 分隔第一个冒号（支持中英文冒号）
    const firstColon = line.search(/[:：]/);
    if (firstColon === -1) {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "system",
        role: "own",
        content: line,
      });
      return;
    }

    const typeStr = line.substring(0, firstColon).trim();
    const rest = line.substring(firstColon + 1).trim();

    // 顶部配置项解析：
    if (typeStr === "机型" || typeStr === "手机机型") {
      if (rest.includes("华为") || rest.includes("junxiu")) {
        if (systemStore?.appearance) {
          systemStore.appearance.model = "huawei_junxiu";
        }
      } else if (rest.includes("默认") || rest.includes("安卓") || rest.includes("android")) {
        if (systemStore?.appearance) {
          systemStore.appearance.model = "android";
        }
      }
      return;
    }

    if (typeStr === "手机时间") {
      const match = rest.match(/(\d{1,2})[:：](\d{1,2})/);
      if (match && systemStore?.appearance) {
        systemStore.appearance.phoneTimeHour = match[1].padStart(2, "0");
        systemStore.appearance.phoneTimeMinute = match[2].padStart(2, "0");
        systemStore.appearance.timeFollowSystem = false;
      }
      return;
    }

    if (typeStr === "手机电量" || typeStr === "电量") {
      const match = rest.match(/\d+/);
      if (match && systemStore?.appearance) {
        systemStore.appearance.phoneBattery = Math.min(100, Math.max(0, parseInt(match[0], 10)));
      }
      return;
    }

    if (typeStr === "对方用户名" || typeStr === "对方昵称" || typeStr === "对方姓名") {
      const nickname = rest.trim();
      if (nickname) {
        defaultOther.nickname = nickname;
        if (others.length > 0) {
          others[0].nickname = nickname;
        } else if (userList.length > 1) {
          userList[1].nickname = nickname;
        } else if (userList.length === 1) {
          defaultOther = {
            id: "user-" + Date.now(),
            nickname: nickname,
            role: "other",
          };
          userStore.userList.push(defaultOther);
        }
        if (userStore?.activeUser && userStore?.activeRole === "other") {
          userStore.activeUser.nickname = nickname;
        }
        if (systemStore?.appearance) {
          systemStore.appearance.chatTitle = nickname;
        }
      }
      return;
    }

    // 单段消息类型（无发送者）：时间、系统、拍一拍
    if (typeStr === "时间") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "time",
        content: rest.replace(/(^|[^\d])0([1-9][:：]\d{2})/g, '$1$2'),
      });
      return;
    }

    if (typeStr === "系统") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "system",
        role: "own",
        content: rest,
      });
      return;
    }

    if (typeStr === "拍一拍") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "takeAPat",
        content: rest,
        patBold: true,
      });
      return;
    }

    // 含有发送者的消息类型：类型：发送者：内容/参数
    const secondColon = rest.search(/[:：]/);
    let senderStr = "";
    let bodyStr = "";
    if (secondColon === -1) {
      senderStr = rest;
      bodyStr = "";
    } else {
      senderStr = rest.substring(0, secondColon).trim();
      bodyStr = rest.substring(secondColon + 1).trim();
    }

    const { role, user } = matchUserAndRole(senderStr);

    if (typeStr === "撤回") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "revoke",
        role,
        user,
        content: "撤回了一条消息",
      });
      return;
    }

    if (typeStr.startsWith("文本") || typeStr.startsWith("文字")) {
      const rejected = typeStr.includes("拒收");
      const content = bodyStr.replace(/\\n/g, "\n");
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "text",
        role,
        user,
        content,
        rejected,
      });
      return;
    }

    if (typeStr === "语音") {
      // bodyStr 格式："5秒"、"5秒：语音转文字" 或 "5"
      let duration = 2;
      let voiceContent = "";
      const thirdColon = bodyStr.search(/[:：]/);
      let durPart = bodyStr;
      if (thirdColon !== -1) {
        durPart = bodyStr.substring(0, thirdColon).trim();
        voiceContent = bodyStr.substring(thirdColon + 1).trim();
      }
      const match = durPart.match(/\d+/);
      if (match) {
        duration = Math.min(60, Math.max(1, parseInt(match[0], 10)));
      }
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "voice",
        role,
        user,
        duration,
        content: voiceContent,
        received: true,
      });
      return;
    }

    if (typeStr.includes("通话")) {
      const invateType = typeStr.includes("视频") ? "video" : "audio";
      let state = "success";
      let duration = "00:10";

      if (bodyStr.includes("取消")) {
        state = "cancel";
        duration = "已取消";
      } else if (bodyStr.includes("拒绝")) {
        state = "rejected";
        duration = "已拒绝";
      } else if (bodyStr.includes("忙线")) {
        state = "busy";
        duration = "忙线未接听";
      } else if (bodyStr.includes("未接")) {
        state = "notConnect";
        duration = "未接听";
      } else {
        state = "success";
        const timeMatch = bodyStr.match(/(\d{1,2}:\d{2}(?::\d{2})?)/);
        if (timeMatch) {
          duration = timeMatch[1];
        } else {
          const secMatch = bodyStr.match(/(\d+)\s*秒?/);
          if (secMatch) {
            const secs = parseInt(secMatch[1], 10);
            const m = String(Math.floor(secs / 60)).padStart(2, "0");
            const s = String(secs % 60).padStart(2, "0");
            duration = `${m}:${s}`;
          }
        }
      }

      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "avInvite",
        role,
        user,
        invateType,
        duration,
        state,
      });
      return;
    }

    if (typeStr === "转账") {
      let money = 88;
      let remarks = "";
      const thirdColon = bodyStr.search(/[:：]/);
      let moneyPart = bodyStr;
      if (thirdColon !== -1) {
        moneyPart = bodyStr.substring(0, thirdColon).trim();
        remarks = bodyStr.substring(thirdColon + 1).trim();
      }
      const match = moneyPart.match(/[\d.]+/);
      if (match) {
        money = parseFloat(match[0]) || 88;
      }
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "transferAccounts",
        role,
        user,
        money,
        content: remarks,
        received: false,
      });
      return;
    }

    if (typeStr === "转账收款" || typeStr === "收款") {
      let money = 88;
      const match = bodyStr.match(/[\d.]+/);
      if (match) {
        money = parseFloat(match[0]) || 88;
      }
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "receive",
        receivedChatType: "transferAccounts",
        role,
        user,
        money,
      });
      return;
    }

    if (typeStr === "红包") {
      let money = 88;
      let remarks = "恭喜发财，大吉大利";
      const thirdColon = bodyStr.search(/[:：]/);
      if (thirdColon !== -1) {
        const moneyPart = bodyStr.substring(0, thirdColon).trim();
        remarks = bodyStr.substring(thirdColon + 1).trim() || remarks;
        const match = moneyPart.match(/[\d.]+/);
        if (match) money = parseFloat(match[0]) || 88;
      } else {
        const match = bodyStr.match(/^[\d.]+\s*元?$/);
        if (match) {
          money = parseFloat(match[0]) || 88;
        } else if (bodyStr) {
          remarks = bodyStr;
        }
      }
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "redEnvelope",
        role,
        user,
        money,
        content: remarks,
        received: false,
      });
      return;
    }

    if (typeStr === "红包领取") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "receive",
        receivedChatType: "redEnvelope",
        role,
        user,
      });
      return;
    }

    if (typeStr === "图片") {
      let imgUrl = bodyStr;
      if (!imgUrl || imgUrl === "[图片]" || (!imgUrl.startsWith("http") && !imgUrl.startsWith("data:"))) {
        imgUrl = "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=400";
      }
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "image",
        role,
        user,
        content: imgUrl,
      });
      return;
    }

    if (typeStr === "名片") {
      result.push({
        id: `chat-${baseTimestamp}-${idx}`,
        type: "businessCard",
        role,
        user,
        content: bodyStr || "个人名片",
        image: otherAvatar,
      });
      return;
    }

    // 默认作为文本处理
    result.push({
      id: `chat-${baseTimestamp}-${idx}`,
      type: "text",
      role,
      user,
      content: bodyStr || rest || "",
    });
  });

  return result;
}

/**
 * 依据特殊符号划分多张图片的文本块
 * 支持的分隔符号包括：
 * --- 或 === (连续3个及以上)
 * --- 图1 --- 或 === 图2 ===
 * 【图片1】 或 [图片1]
 */
export function splitBatchText(rawText = "") {
  if (!rawText) return [];
  const lines = String(rawText).split(/\r?\n/);
  const chunks = [];
  let currentLines = [];

  const isDelimiter = (line) => {
    const trimmed = line.trim();
    if (!trimmed) return false;
    if (/^[-=]{3,}$/.test(trimmed)) return true;
    if (/^---.*?---$/.test(trimmed)) return true;
    if (/^===.*?===$/.test(trimmed)) return true;
    if (/^(【|\[)(?:图片|图|page|split).*?(】|\])$/i.test(trimmed)) return true;
    return false;
  };

  for (const line of lines) {
    if (isDelimiter(line)) {
      if (currentLines.some((l) => l.trim())) {
        chunks.push(currentLines.join("\n").trim());
        currentLines = [];
      }
    } else {
      currentLines.push(line);
    }
  }

  if (currentLines.some((l) => l.trim())) {
    chunks.push(currentLines.join("\n").trim());
  }

  return chunks;
}

/**
 * 解析批量文本为任务对象列表
 */
export function parseBatchTasks(rawText = "", baseAppearance = {}, options = {}) {
  const chunks = splitBatchText(rawText);
  if (!chunks.length) return [];

  let currentAppearance = { ...baseAppearance };
  const userStore = options.userStore;

  const tasks = chunks.map((chunk, index) => {
    // 构造模拟的 systemStore，用于承接当前 chunk 内部可能存在的顶部描述
    const systemStoreMock = {
      appearance: { ...currentAppearance },
    };

    const chatList = textToChatList(chunk, {
      userStore,
      systemStore: systemStoreMock,
    });

    // 继承或更新 appearance
    currentAppearance = { ...systemStoreMock.appearance };

    return {
      id: `task-${Date.now()}-${index}`,
      title: `图 ${index + 1}`,
      rawText: chunk,
      appearance: { ...systemStoreMock.appearance },
      chatList: chatList || [],
      status: "idle", // 'idle' | 'generating' | 'done' | 'error'
      generatedImage: "",
    };
  });

  return tasks;
}

/**
 * 将任务对象序列化为单个文本块
 */
export function taskToText(task, options = {}) {
  if (!task) return "";
  return chatListToText(task.chatList || [], {
    systemStore: { appearance: task.appearance || {} },
    userStore: options.userStore,
  });
}

/**
 * 将多个任务合并为批量文本，使用 --- 符号隔开
 */
export function batchTasksToText(tasks = [], options = {}) {
  if (!Array.isArray(tasks) || !tasks.length) return "";
  return tasks
    .map((task) => taskToText(task, options))
    .join("\n\n---\n\n");
}

