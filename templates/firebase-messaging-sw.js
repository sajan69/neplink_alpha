importScripts('https://www.gstatic.com/firebasejs/8.6.8/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.6.8/firebase-messaging.js');

firebase.initializeApp({
    apiKey: "AIzaSyBSQZPpLOHznojHh9R_OaeHBjvr92CzLkg",
  authDomain: "neplink.firebaseapp.com",
  databaseURL: "https://neplink-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "neplink",
  storageBucket: "neplink.appspot.com",
  messagingSenderId: "424450153128",
  appId: "1:424450153128:web:14068d82d2c5791891809d",
  measurementId: "G-FW9V6B9SND"
});

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: payload.notification.icon
    };
    return self.registration.showNotification(notificationTitle, notificationOptions);
});
