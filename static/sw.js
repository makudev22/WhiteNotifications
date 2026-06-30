self.addEventListener("push", function (event) {
  var data = { title: "WhiteNotifications", body: "new message" };
  if (event.data) {
    try { data = event.data.json(); } catch (e) {}
  }
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    data: { url: data.url || "/" }
  }));
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  var url = event.notification.data && event.notification.data.url ? event.notification.data.url : "/";
  event.waitUntil(clients.openWindow(url).catch(function () {
    return clients.openWindow("/");
  }));
});
