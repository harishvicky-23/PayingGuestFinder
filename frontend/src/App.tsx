import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

// Pages
import { HomePage } from './pages/HomePage';
import { ExplorePage } from './pages/ExplorePage';
import { PropertyDetailPage } from './pages/PropertyDetailPage';
import { BookingsPage } from './pages/BookingsPage';
import { FavouritesPage } from './pages/FavouritesPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

// Host Pages
import { HostDashboardPage } from './pages/host/HostDashboardPage';
import { HostPropertiesPage } from './pages/host/HostPropertiesPage';
import { CreatePropertyPage } from './pages/host/CreatePropertyPage';
import { HostAnalyticsPage } from './pages/host/HostAnalyticsPage';

// MLOps
import { MLOpsDashboardPage } from './pages/admin/MLOpsDashboardPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="flex flex-col min-h-screen bg-slate-50">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/properties/:id" element={<PropertyDetailPage />} />
              <Route path="/bookings" element={<BookingsPage />} />
              <Route path="/favourites" element={<FavouritesPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Host routes */}
              <Route path="/host/dashboard" element={<HostDashboardPage />} />
              <Route path="/host/properties" element={<HostPropertiesPage />} />
              <Route path="/host/properties/new" element={<CreatePropertyPage />} />
              <Route path="/host/analytics" element={<HostAnalyticsPage />} />

              {/* MLOps admin route */}
              <Route path="/admin/ml-operations" element={<MLOpsDashboardPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
