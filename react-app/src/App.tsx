import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect, Suspense, lazy } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'react-hot-toast';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorFallback from './components/ErrorFallback';
import { AuthProvider } from './context/AuthContext';
import { AnalyticsProvider } from './context/AnalyticsContext';
import { ThemeProvider } from './context/ThemeContext';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Summarizer = lazy(() => import('./pages/Summarizer'));
const TeamSearch = lazy(() => import('./pages/TeamSearch'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Profile = lazy(() => import('./pages/Profile'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading time and check for cached data
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <HelmetProvider>
        <ThemeProvider>
          <AuthProvider>
            <AnalyticsProvider>
              <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
                  <Navigation />
                  <main className="container mx-auto px-4 py-8">
                    <Suspense fallback={<LoadingSpinner />}>
                      <Routes>
                        {/* Public routes - no authentication required */}
                        <Route path="/login" element={
                          <PublicRoute>
                            <Login />
                          </PublicRoute>
                        } />
                        <Route path="/register" element={
                          <PublicRoute>
                            <Register />
                          </PublicRoute>
                        } />
                        
                        {/* Protected routes - authentication required */}
                        <Route path="/" element={
                          <ProtectedRoute>
                            <Home />
                          </ProtectedRoute>
                        } />
                        <Route path="/summarizer" element={
                          <ProtectedRoute>
                            <Summarizer />
                          </ProtectedRoute>
                        } />
                        <Route path="/search" element={
                          <ProtectedRoute>
                            <TeamSearch />
                          </ProtectedRoute>
                        } />
                        <Route path="/analytics" element={
                          <ProtectedRoute>
                            <Analytics />
                          </ProtectedRoute>
                        } />
                        <Route path="/profile" element={
                          <ProtectedRoute>
                            <Profile />
                          </ProtectedRoute>
                        } />
                        
                        {/* 404 route */}
                        <Route path="*" element={
                          <div className="flex flex-col items-center justify-center min-h-[60vh]">
                            <h1 className="text-6xl font-bold text-gray-300 dark:text-gray-600 mb-4">404</h1>
                            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">Page not found</p>
                            <button 
                              onClick={() => window.history.back()}
                              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                              Go Back
                            </button>
                          </div>
                        } />
                      </Routes>
                    </Suspense>
                  </main>
                </div>
              </Router>
              
              {/* Global toast notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#10B981',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#EF4444',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </AnalyticsProvider>
          </AuthProvider>
        </ThemeProvider>
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App;
