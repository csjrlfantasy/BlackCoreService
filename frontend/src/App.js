import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import HierarchyForm from './components/HierarchyForm';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Profile />} />
      <Route path="/" element={<Login />} />
      
      {/* 新增表单路由 */}
      <Route path="/hierarchy-form" element={<HierarchyForm />} />
    </Routes>
  );
}

export default App;