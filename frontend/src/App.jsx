import { Routes, Route } from 'react-router-dom';
import FormDemo from './components/FormDemo';

function App() {
  return (
    <Routes>
      {/* 原有路由... */}
      <Route path="/form-demo" element={<FormDemo />} />
    </Routes>
  );
}
