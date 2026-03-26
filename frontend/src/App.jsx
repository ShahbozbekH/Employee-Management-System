import './App.css';
import Login from './Login';
import Success from './Success';
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="main-layout">
      <aside className="taskbar">
        <h2>Taskbar</h2>
        <ul>
          <li>Home</li>
          <li>Login</li>
          <li>About</li>
        </ul>
      </aside>
      <main className="center-content">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/success" element={<Success />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
