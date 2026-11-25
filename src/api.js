import axios from 'axios';
// https://api.goutou.club
// http://127.0.0.1:10002
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.goutou.club';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  },
  // Removed transformRequest because it was stripping quotes from college_id and course_id
  transformResponse: [function (data) {
    if (typeof data === 'string') {
      try {
        // Fix JavaScript int64 precision loss by wrapping large IDs in quotes before parsing
        const fixedData = data.replace(/"([a-zA-Z0-9_]*id)":\s*(\d{15,20})/gi, '"$1":"$2"');
        return JSON.parse(fixedData);
      } catch (e) {
        return data;
      }
    }
    return data;
  }]
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * 供全站调用的无感/主动 Token 刷新方法，使用 7 天 RefreshToken 换取新的双 Token
 */
export const refreshAccessToken = async () => {
  const oldRefreshToken = localStorage.getItem('refresh_token') || '';
  if (!oldRefreshToken) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_nickname');
    localStorage.removeItem('user_id');
    window.dispatchEvent(new Event('auth-expired'));
    throw new Error('未找到有效的 RefreshToken，请重新登录');
  }

  try {
    const refreshResponse = await axios.post(`${BASE_URL}/user/refresh_token`, {
      refresh_token: oldRefreshToken
    }, {
      headers: {
        'X-Refresh-Token': oldRefreshToken
      },
      withCredentials: true
    });

    let data = refreshResponse.data;
    if (data.errCode === 0 && data.data) {
      data = data.data;
    }

    const newAccessToken = data.accessToken || data.access_token;
    const newRefreshToken = data.refreshToken || data.refresh_token;

    if (newAccessToken) {
      localStorage.setItem('access_token', newAccessToken);
      if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken);
      }
      api.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;
      return newAccessToken;
    } else {
      throw new Error('服务器未返回有效 Token');
    }
  } catch (err) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_nickname');
    localStorage.removeItem('user_id');
    window.dispatchEvent(new Event('auth-expired'));
    throw err;
  }
};

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    // Intercept backend custom token errors (e.g. 1001) that return 200 OK
    if (response.data && response.data.errCode === 1001 && response.data.errMsg && response.data.errMsg.includes('access_token')) {
      const customErr = new Error(response.data.errMsg);
      customErr.response = { status: 401, data: response.data };
      customErr.config = response.config;
      return Promise.reject(customErr);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Check if error is 401 and we haven't retried yet, and not the refresh endpoint itself
    if (error.response && error.response.status === 401 && !originalRequest._retry && (!originalRequest.url || !originalRequest.url.includes('/user/refresh_token'))) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccessToken = await refreshAccessToken();
        processQueue(null, newAccessToken);
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
