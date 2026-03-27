import './App.css';
import Login from './Login';
import Success from './Success';
import Register from './Register';
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="main-layout">
      <aside className="taskbar">
        <h2>Taskbar</h2>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/register">Register</a></li>
        </ul>
      </aside>
      <main className="center-content">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/success" element={<Success />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
