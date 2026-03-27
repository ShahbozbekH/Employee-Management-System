import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

import Login from './Login'

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
  },
}))

import axios from 'axios'

function renderWithRouter(ui) {
  return render(<BrowserRouter>{ui}</BrowserRouter>)
}

describe('Login Page', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('renders login form correctly', () => {
    renderWithRouter(<Login />)
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    renderWithRouter(<Login />)
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    expect(await screen.findByText(/username is required/i)).toBeInTheDocument()
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument()
  })

  it('displays error message when login fails', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { message: 'Invalid credentials' } } })
    renderWithRouter(<Login />)
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpassword')
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument()
  })

  it('successful login stores JWT and role in localStorage', async () => {
    axios.post.mockResolvedValueOnce({
      status: 200,
      data: { access_token: 'fake-jwt', role: 'admin' },
    })
    renderWithRouter(<Login />)
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/password/i), 'StrongPassw0rd!')
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('fake-jwt')
      expect(localStorage.getItem('role')).toBe('admin')
    })
  })

  it('redirects to home page on successful login', async () => {
    axios.post.mockResolvedValueOnce({
      status: 200,
      data: { access_token: 'fake-jwt', role: 'admin' },
    })
    renderWithRouter(<Login />)
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/password/i), 'StrongPassw0rd!')
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/success')
    })
  })

  it('shows loading indicator during login', async () => {
    // Optionally, you can add a loading state to Login and test for it here
    // For now, just simulate a slow response
    let resolvePromise
    axios.post.mockImplementationOnce(() => new Promise(res => { resolvePromise = res }))
    renderWithRouter(<Login />)
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/password/i), 'StrongPassw0rd!')
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    // If you add a loading spinner, check for it here
    // expect(screen.getByTestId('loading')).toBeInTheDocument()
    resolvePromise({ status: 200, data: { access_token: 'jwt', role: 'user' } })
  })

  it('does not submit if fields are empty', async () => {
    renderWithRouter(<Login />)
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    expect(await screen.findByText(/username is required/i)).toBeInTheDocument()
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument()
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('trims username and password before sending', async () => {
    axios.post.mockResolvedValueOnce({
      status: 200,
      data: { access_token: 'jwt', role: 'user' },
    })
    renderWithRouter(<Login />)
    await userEvent.type(screen.getByLabelText(/username/i), '  testuser  ')
    await userEvent.type(screen.getByLabelText(/password/i), '  password  ')
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    await waitFor(() => {
      // Check that axios.post was called with URLSearchParams containing trimmed values
      expect(axios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(URLSearchParams),
        expect.any(Object)
      )
      const params = axios.post.mock.calls[0][1];
      expect(params.get('username')).toBe('testuser');
      expect(params.get('password')).toBe('password');
    })
  })
})