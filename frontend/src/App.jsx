import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { NotificationProvider } from './context/NotificationContext'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import PublicLayout from './layouts/PublicLayout'
import AuthenticatedLayout from './layouts/AuthenticatedLayout'
import AdminLayout from './layouts/AdminLayout'
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
import WorkoutTracker from './pages/WorkoutTracker'
import MealDiary from './pages/MealDiary'
import AdminUsers from './pages/admin/AdminUsers'
import AdminFoods from './pages/admin/AdminFoods'
import AdminExercises from './pages/admin/AdminExercises'
import AdminBodyTypes from './pages/admin/AdminBodyTypes'
import AdminBmiCategories from './pages/admin/AdminBmiCategories'

function App() {
  return (
    <NotificationProvider>
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
              <Route
                path="/workout-tracker"
                element={
                  <ProtectedRoute>
                    <AuthenticatedLayout>
                      <WorkoutTracker />
                    </AuthenticatedLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/meal-diary"
                element={
                  <ProtectedRoute>
                    <AuthenticatedLayout>
                      <MealDiary />
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
                      <AdminUsers />
                    </AdminLayout>
                  </AdminRoute>
                }
              />
              <Route
                path="/admin/foods"
                element={
                  <AdminRoute>
                    <AdminLayout>
                      <AdminFoods />
                    </AdminLayout>
                  </AdminRoute>
                }
              />
              <Route
                path="/admin/exercises"
                element={
                  <AdminRoute>
                    <AdminLayout>
                      <AdminExercises />
                    </AdminLayout>
                  </AdminRoute>
                }
              />
              <Route
                path="/admin/body-types"
                element={
                  <AdminRoute>
                    <AdminLayout>
                      <AdminBodyTypes />
                    </AdminLayout>
                  </AdminRoute>
                }
              />
              <Route
                path="/admin/bmi-categories"
                element={
                  <AdminRoute>
                    <AdminLayout>
                      <AdminBmiCategories />
                    </AdminLayout>
                  </AdminRoute>
                }
              />
            </Routes>
          </PublicLayout>
        </BrowserRouter>
      </AuthProvider>
    </NotificationProvider>
  )
}

export default App
