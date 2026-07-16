import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import PublicLayout from './layouts/PublicLayout'
import LandingPage from './pages/LandingPage'
import About from './pages/About'
import Contact from './pages/Contact'
import ComingSoon from './pages/ComingSoon'
import BMICalculator from './pages/BMICalculator'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <PublicLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route
              path="/healthy-foods"
              element={
                <ComingSoon
                  title="Healthy Foods"
                  description="Sri Lankan meal plans and nutrition breakdowns are on their way."
                />
              }
            />
            <Route
              path="/workouts"
              element={
                <ComingSoon
                  title="Workouts"
                  description="Workout plan details and weekly schedules are on their way."
                />
              }
            />
            <Route path="/bmi-calculator" element={<BMICalculator />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
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
