import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Register from './Register';

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
  },
}));
import axios from 'axios';

function renderWithRouter(ui) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe('Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders registration form correctly', () => {
    renderWithRouter(<Register />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  it('validates password match', async () => {
    renderWithRouter(<Register />);
    await userEvent.type(screen.getByLabelText(/username/i), 'newuser');
    await userEvent.type(screen.getByLabelText(/email/i), 'new@user.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pass1');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'pass2');
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
  });

  it('displays error message when registration fails', async () => {
    axios.post.mockRejectedValueOnce({ response: { data: { message: 'User already exists' } } });
    renderWithRouter(<Register />);
    await userEvent.type(screen.getByLabelText(/username/i), 'existinguser');
    await userEvent.type(screen.getByLabelText(/email/i), 'exist@user.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'password');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'password');
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByText(/user already exists/i)).toBeInTheDocument();
  });

  it('successful registration redirects to home', async () => {
    axios.post.mockResolvedValueOnce({ status: 201 });
    renderWithRouter(<Register />);
    await userEvent.type(screen.getByLabelText(/username/i), 'newuser');
    await userEvent.type(screen.getByLabelText(/email/i), 'new@user.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'password');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'password');
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
