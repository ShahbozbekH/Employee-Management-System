import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState({ username: false, password: false });

  const validate = () => {
    const errors = {};
    if (!username) errors.username = 'Username is required';
    if (!password) errors.password = 'Password is required';
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTouched({ username: true, password: true });
    const errors = validate();
    if (Object.keys(errors).length > 0) return;
    try {
      const params = new URLSearchParams();
      params.append('username', username.trim());
      params.append('password', password.trim());
      const response = await axios.post('http://localhost:8000/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      if (response.status === 200) {
        const { access_token, role } = response.data;
        localStorage.setItem('token', access_token);
        localStorage.setItem('role', role);
        setError('');
        if (onLogin) onLogin();
        navigate('/success'); // Redirect to success page after login
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError('Login failed');
      }
    }
  };

  const errors = validate();

  return (
    <div className="login-box">
      <h1>Login</h1>
      {error && <div style={{ color: 'red', marginBottom: '1em' }}>{error}</div>}
      <form className="login-form" onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          name="username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          onBlur={() => setTouched(t => ({ ...t, username: true }))}
        />
        {touched.username && errors.username && (
          <span style={{ color: 'red' }}>{errors.username}</span>
        )}
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onBlur={() => setTouched(t => ({ ...t, password: true }))}
        />
        {touched.password && errors.password && (
          <span style={{ color: 'red' }}>{errors.password}</span>
        )}
        <button type="submit">Login</button>
      </form>
    </div>
  );
}
