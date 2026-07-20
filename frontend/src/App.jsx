import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import PublicLayout from './layouts/PublicLayout'
import AuthenticatedLayout from './layouts/AuthenticatedLayout'
import LandingPage from './pages/LandingPage'
import About from './pages/About'
import Contact from './pages/Contact'
import BMICalculator from './pages/BMICalculator'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Dashboard from './pages/Dashboard'
import ImageAnalysis from './pages/ImageAnalysis'
import HealthyFoods from './pages/HealthyFoods'
import MealPlanDetail from './pages/MealPlanDetail'
import Workouts from './pages/Workouts'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <PublicLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/healthy-foods" element={<HealthyFoods />} />
            <Route path="/workouts" element={<Workouts />} />
            <Route path="/bmi-calculator" element={<BMICalculator />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <Dashboard />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <Profile />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analyze"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <ImageAnalysis />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/meal-plan"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <MealPlanDetail />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </PublicLayout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
