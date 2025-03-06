import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  // Copy these values from your Firebase Console -> Project Settings -> Web configuration
  apiKey: "your-api-key",
  authDomain: "reflectify-f63aa.firebaseapp.com",
  projectId: "reflectify-f63aa",
  storageBucket: "reflectify-f63aa.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app); 