// Service Worker for Web Push Notifications
// 科研日报推送通知服务

const CACHE_NAME = 'rss-daily-report-v1';
const urlsToCache = [
  '/latest.html'
];

// 安装事件 - 缓存资源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// 推送事件 - 接收并显示通知
self.addEventListener('push', event => {
  console.log('[Service Worker] Push 接收:', event);

  let notificationData = {
    title: '科研日报更新',
    body: '今日科研日报已生成，点击查看最新内容',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    tag: 'daily-report',
    requireInteraction: false,
    data: {
      url: '/latest.html',
      date: new Date().toISOString()
    }
  };

  // 如果推送带有数据，解析并使用
  if (event.data) {
    try {
      const payload = event.data.json();
      notificationData = {
        ...notificationData,
        ...payload
      };
    } catch (e) {
      console.log('[Service Worker] 推送数据解析失败，使用默认配置');
    }
  }

  const promiseChain = self.registration.showNotification(
    notificationData.title,
    {
      body: notificationData.body,
      icon: notificationData.icon,
      badge: notificationData.badge,
      tag: notificationData.tag,
      requireInteraction: notificationData.requireInteraction,
      data: notificationData.data,
      actions: [
        {
          action: 'open',
          title: '查看详情'
        },
        {
          action: 'close',
          title: '关闭'
        }
      ]
    }
  );

  event.waitUntil(promiseChain);
});

// 通知点击事件
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] 通知点击:', event.action);

  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  // 打开或聚焦到 latest.html 页面
  const urlToOpen = new URL(event.notification.data.url || '/latest.html', self.location.origin).href;

  const promiseChain = clients.matchAll({
    type: 'window',
    includeUncontrolled: true
  })
  .then(windowClients => {
    // 检查是否已有打开的页面
    for (let i = 0; i < windowClients.length; i++) {
      const client = windowClients[i];
      if (client.url === urlToOpen && 'focus' in client) {
        return client.focus();
      }
    }
    // 如果没有，打开新页面
    if (clients.openWindow) {
      return clients.openWindow(urlToOpen);
    }
  });

  event.waitUntil(promiseChain);
});

// Fetch 事件 - 提供缓存优先策略（可选）
self.addEventListener('fetch', event => {
  // 对于 HTML 页面，使用网络优先策略
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 其他资源使用缓存优先
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
