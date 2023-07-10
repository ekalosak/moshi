// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-analytics.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDLqltqpYoJ7OmMu216rX8oGQadx2zM8mY",
  authDomain: "moshi-002.firebaseapp.com",
  projectId: "moshi-002",
  storageBucket: "moshi-002.appspot.com",
  messagingSenderId: "462213871057",
  appId: "1:462213871057:web:a25b22832e16adc5a19cf0",
  measurementId: "G-FFF1BC04WY"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

// Export JS objects
export {
   app,
   analytics,
   auth,
};

window.auth = auth;
