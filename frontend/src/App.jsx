import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence, MotionConfig } from 'framer-motion'
import { AuthProvider } from './context/AuthContext'
import { NotificationProvider } from './context/NotificationContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import PageTransition from './components/PageTransition'
import PublicLayout from './layouts/PublicLayout'
import AuthenticatedLayout from './layouts/AuthenticatedLayout'
import AdminLayout from './layouts/AdminLayout'
import LandingPage from './pages/LandingPage'
import About from './pages/About'
import Contact from './pages/Contact'
import Terms from './pages/Terms'
import Privacy from './pages/Privacy'
import NotFound from './pages/NotFound'
import BMICalculator from './pages/BMICalculator'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Dashboard from './pages/Dashboard'
import ImageAnalysis from './pages/ImageAnalysis'
import HealthyFoods from './pages/HealthyFoods'
import MealPlanDetail from './pages/MealPlanDetail'
import Workouts from './pages/Workouts'
import WorkoutTracker from './pages/WorkoutTracker'
import MealDiary from './pages/MealDiary'
import AdminUsers from './pages/admin/AdminUsers'
import AdminFoods from './pages/admin/AdminFoods'
import AdminExercises from './pages/admin/AdminExercises'
import AdminBodyTypes from './pages/admin/AdminBodyTypes'
import AdminBmiCategories from './pages/admin/AdminBmiCategories'

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageTransition><LandingPage /></PageTransition>} />
        <Route path="/about" element={<PageTransition><About /></PageTransition>} />
        <Route path="/contact" element={<PageTransition><Contact /></PageTransition>} />
        <Route path="/terms" element={<PageTransition><Terms /></PageTransition>} />
        <Route path="/privacy" element={<PageTransition><Privacy /></PageTransition>} />
        <Route path="/healthy-foods" element={<PageTransition><HealthyFoods /></PageTransition>} />
        <Route path="/workouts" element={<PageTransition><Workouts /></PageTransition>} />
        <Route path="/bmi-calculator" element={<PageTransition><BMICalculator /></PageTransition>} />
        <Route path="/login" element={<PageTransition><Login /></PageTransition>} />
        <Route path="/register" element={<PageTransition><Register /></PageTransition>} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <Dashboard />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <Profile />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analyze"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <ImageAnalysis />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/meal-plan"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <MealPlanDetail />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/workout-tracker"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <WorkoutTracker />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/meal-diary"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageTransition>
                  <MealDiary />
                </PageTransition>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route path="/admin" element={<Navigate to="/admin/users" replace />} />
        <Route
          path="/admin/users"
          element={
            <AdminRoute>
              <AdminLayout>
                <PageTransition>
                  <AdminUsers />
                </PageTransition>
              </AdminLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/admin/foods"
          element={
            <AdminRoute>
              <AdminLayout>
                <PageTransition>
                  <AdminFoods />
                </PageTransition>
              </AdminLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/admin/exercises"
          element={
            <AdminRoute>
              <AdminLayout>
                <PageTransition>
                  <AdminExercises />
                </PageTransition>
              </AdminLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/admin/body-types"
          element={
            <AdminRoute>
              <AdminLayout>
                <PageTransition>
                  <AdminBodyTypes />
                </PageTransition>
              </AdminLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/admin/bmi-categories"
          element={
            <AdminRoute>
              <AdminLayout>
                <PageTransition>
                  <AdminBmiCategories />
                </PageTransition>
              </AdminLayout>
            </AdminRoute>
          }
        />
        <Route path="*" element={<PageTransition><NotFound /></PageTransition>} />
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <BrowserRouter>
            <MotionConfig reducedMotion="user">
              <PublicLayout>
                <AnimatedRoutes />
              </PublicLayout>
            </MotionConfig>
          </BrowserRouter>
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  )
}

export default App
