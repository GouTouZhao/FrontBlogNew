import { createPinia } from "pinia";
import piniaPluginPersist from "pinia-plugin-persist";

// 自定义 IndexedDB 持久化插件 (突破 5MB 限制，强制兼容)
function indexedDBPersistPlugin({ store, options }) {
  if (options.persistDB) {
    const DB_NAME = 'WeChatToolDB';
    const STORE_NAME = 'pinia-store';

    const getDB = () => new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = (e) => e.target.result.createObjectStore(STORE_NAME);
      request.onsuccess = (e) => resolve(e.target.result);
      request.onerror = (e) => reject(e.target.error);
    });

    const key = store.$id;
    const paths = options.persistDB.paths;

    // 1. 异步恢复数据（并平滑迁移爆满的 localStorage 旧数据）
    getDB().then(db => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const req = tx.objectStore(STORE_NAME).get(key);
      req.onsuccess = () => {
        if (req.result) {
          store.$patch(req.result);
        } else {
          // 第一次使用 DB，尝试从 localStorage 抢救之前被存下的遗留数据
          const oldData = localStorage.getItem(key);
          if (oldData) {
            try { store.$patch(JSON.parse(oldData)); } catch (e) {}
          }
        }
        // 清理掉 localStorage 里的超大键值，瞬间解除 5MB 限制报错！
        localStorage.removeItem(key);
      };
    }).catch(err => console.warn('IndexedDB Load Error:', err));

    // 2. 监听改变并高容量保存
    store.$subscribe((mutation, state) => {
      let dataToSave = JSON.parse(JSON.stringify(state));
      if (paths && paths.length) {
        dataToSave = {};
        paths.forEach(p => {
          dataToSave[p] = JSON.parse(JSON.stringify(state[p]));
        });
      }
      getDB().then(db => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        tx.objectStore(STORE_NAME).put(dataToSave, key);
      }).catch(err => console.warn('IndexedDB Save Error:', err));
    });
  }
}

// 创建pinia实例
const pinia = createPinia();
// 保留原始的持久化以兼容小 store
pinia.use(piniaPluginPersist);
// 注入我们的强制大容量持久化插件
pinia.use(indexedDBPersistPlugin);

export default pinia;
