import React, { useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import useAppStore from './store/appStore'
import Onboarding from './pages/Onboarding'
import Feed from './pages/Feed'
import Player from './pages/Player'
import Profile from './pages/Profile'

function RequireUser({ children }) {
  const user = useAppStore((s) => s.user)
  if (!user) {
    return <Navigate to="/onboarding" replace />
  }
  return children
}

function RootRedirect() {
  const user = useAppStore((s) => s.user)
  return <Navigate to={user ? '/feed' : '/onboarding'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route
        path="/feed"
        element={
          <RequireUser>
            <Feed />
          </RequireUser>
        }
      />
      <Route
        path="/player"
        element={
          <RequireUser>
            <Player />
          </RequireUser>
        }
      />
      <Route
        path="/profile"
        element={
          <RequireUser>
            <Profile />
          </RequireUser>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
