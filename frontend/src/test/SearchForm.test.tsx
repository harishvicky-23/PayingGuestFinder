import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { AuthProvider } from '../context/AuthContext';

describe('Search Form & Discovery', () => {
  it('renders landing hero and search inputs', () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <HomePage />
        </BrowserRouter>
      </AuthProvider>
    );

    expect(screen.getByText(/Find the right space, for/)).toBeInTheDocument();
    expect(screen.getByText('Guindy (Metro & Tech Park)')).toBeInTheDocument();
    expect(screen.getByText('Hourly (1–4 hrs)')).toBeInTheDocument();
    expect(screen.getByText('Find Spaces')).toBeInTheDocument();
  });
});
