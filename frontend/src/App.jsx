import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PublicLayout from './layouts/PublicLayout'
import LandingPage from './pages/LandingPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <PublicLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
          </Routes>
        </PublicLayout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
