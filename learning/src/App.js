import React from 'react';
import CourseList from './CourseList';
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm';

function App() {
  return (
    <div>
      <h1>My Learning Platform</h1>
      <LoginForm />
      <RegistrationForm />
      <CourseList />
    </div>
  );
}

export default App;