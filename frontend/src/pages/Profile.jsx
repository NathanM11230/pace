import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Cpu, Trophy, Rocket, Heart, Bot,
  Check, Edit2, Save, LogOut, Loader2,
} from 'lucide-react'
import useAppStore from '../store/appStore'
import { api } from '../api/client'
import CategoryPill from '../components/CategoryPill'
import { BottomNav } from './Feed'

const CATEGORIES = [
  {
    id: 'tech',
    label: 'Tech',
    description: 'AI, startups & gadgets',
    Icon: Cpu,
    color: '#0066FF',
    bg: '#EBF3FF',
  },
  {
    id: 'nba',
    label: 'NBA',
    description: 'Scores, trades & highlights',
    Icon: Trophy,
    color: '#FF6B35',
    bg: '#FFF0EB',
  },
  {
    id: 'space',
    label: 'Space',
    description: 'NASA, SpaceX & beyond',
    Icon: Rocket,
    color: '#7B61FF',
    bg: '#F0EEFF',
  },
  {
    id: 'health',
    label: 'Health',
    description: 'Fitness, nutrition & wellness',
    Icon: Heart,
    color: '#00D9A3',
    bg: '#E6FAF5',
  },
  {
    id: 'ai',
    label: 'AI',
    description: 'Machine learning & ChatGPT',
    Icon: Bot,
    color: '#FF61B6',
    bg: '#FFE8F5',
  },
]

function StatCard({ label, value, unit }) {
  return (
    <div className="flex-1 bg-white rounded-2xl p-4 border border-gray-mid text-center">
      <p className="text-xl font-black text-navy">
        {value}
        {unit && <span className="text-sm font-semibold text-gray-dark ml-1">{unit}</span>}
      </p>
      <p className="text-xs text-gray-dark mt-1">{label}</p>
    </div>
  )
}

export default function Profile() {
  const navigate = useNavigate()
  const { user, setUser, clearUser, feed } = useAppStore()

  const [editMode, setEditMode] = useState(false)
  const [selectedInterests, setSelectedInterests] = useState(user?.interests || [])
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [saveSuccess, setSaveSuccess] = useState(false)

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-light flex items-center justify-center">
        <div className="text-center">
          <p className="text-navy font-semibold mb-4">Not logged in</p>
          <button
            onClick={() => navigate('/onboarding')}
            className="bg-blue text-white px-6 py-3 rounded-xl font-semibold"
          >
            Get Started
          </button>
        </div>
      </div>
    )
  }

  const memberSince = user.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'Recently'

  const toggleInterest = (id) => {
    setSelectedInterests((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleSave = async () => {
    if (selectedInterests.length === 0) return
    setSaving(true)
    setSaveError('')
    setSaveSuccess(false)
    try {
      await api.updateInterests(user.id, selectedInterests)
      setUser({ ...user, interests: selectedInterests })
      setEditMode(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      setSaveError(err.message || 'Failed to save interests')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    clearUser()
    navigate('/onboarding')
  }

  const displayInterests = editMode ? selectedInterests : (user.interests || [])

  return (
    <div className="min-h-screen bg-gray-light flex flex-col">
      <div className="w-full max-w-[480px] mx-auto flex flex-col min-h-screen">

        {/* Header */}
        <div
          className="px-4 pt-12 pb-8 text-center"
          style={{ background: 'linear-gradient(160deg, #1A1F36 0%, #252B45 100%)' }}
        >
          {/* Avatar */}
          <div className="w-20 h-20 rounded-full bg-blue flex items-center justify-center mx-auto mb-4 text-white text-3xl font-black shadow-xl shadow-blue/30">
            {user.name ? user.name[0].toUpperCase() : 'U'}
          </div>

          <h2 className="text-white text-xl font-black mb-1">{user.name}</h2>
          <p className="text-white/50 text-sm mb-1">{user.email}</p>
          <p className="text-white/30 text-xs">Member since {memberSince}</p>
        </div>

        {/* Content */}
        <main className="flex-1 px-4 pb-24 pt-5">

          {/* Stats */}
          <div className="mb-6">
            <h3 className="text-sm font-bold text-navy mb-3 px-1">Your Stats</h3>
            <div className="flex gap-3">
              <StatCard label="Today's Listening" value={Math.min(feed.length, 5)} unit="clips" />
              <StatCard label="This Week" value="12" unit="min" />
              <StatCard label="Streak" value="3" unit="days" />
            </div>
          </div>

          {/* Interests */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3 px-1">
              <h3 className="text-sm font-bold text-navy">My Interests</h3>

              {!editMode ? (
                <button
                  onClick={() => {
                    setSelectedInterests(user.interests || [])
                    setEditMode(true)
                  }}
                  className="flex items-center gap-1.5 text-blue text-xs font-semibold hover:text-blue-600 transition-colors"
                >
                  <Edit2 size={12} />
                  Edit
                </button>
              ) : (
                <button
                  onClick={() => {
                    setEditMode(false)
                    setSelectedInterests(user.interests || [])
                    setSaveError('')
                  }}
                  className="text-gray-dark text-xs font-semibold hover:text-navy transition-colors"
                >
                  Cancel
                </button>
              )}
            </div>

            {/* View mode */}
            {!editMode && (
              <div className="bg-white rounded-2xl p-4 border border-gray-mid">
                {(user.interests || []).length === 0 ? (
                  <p className="text-gray-dark text-sm">No interests selected yet.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {(user.interests || []).map((cat) => (
                      <CategoryPill key={cat} category={cat} size="md" />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Edit mode */}
            {editMode && (
              <div>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {CATEGORIES.map(({ id, label, description, Icon, color, bg }) => {
                    const selected = selectedInterests.includes(id)
                    return (
                      <button
                        key={id}
                        onClick={() => toggleInterest(id)}
                        className={`relative text-left p-4 rounded-2xl border-2 transition-all duration-200 active:scale-95 ${
                          selected
                            ? 'border-blue shadow-md shadow-blue/20'
                            : 'border-gray-mid bg-white hover:border-gray-dark/40'
                        }`}
                        style={selected ? { backgroundColor: '#EBF3FF' } : {}}
                      >
                        {selected && (
                          <div className="absolute top-3 right-3 w-5 h-5 bg-blue rounded-full flex items-center justify-center">
                            <Check size={11} color="white" strokeWidth={3} />
                          </div>
                        )}

                        <div
                          className="w-9 h-9 rounded-xl flex items-center justify-center mb-2"
                          style={{ backgroundColor: bg }}
                        >
                          <Icon size={18} style={{ color }} />
                        </div>

                        <p className="font-bold text-navy text-sm mb-0.5">{label}</p>
                        <p className="text-gray-dark text-xs leading-snug">{description}</p>
                      </button>
                    )
                  })}
                </div>

                {saveError && (
                  <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3 mb-3">
                    {saveError}
                  </div>
                )}

                <button
                  onClick={handleSave}
                  disabled={saving || selectedInterests.length === 0}
                  className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    !saving && selectedInterests.length > 0
                      ? 'bg-blue text-white hover:bg-blue-600 active:scale-95'
                      : 'bg-gray-mid text-gray-dark cursor-not-allowed opacity-60'
                  }`}
                >
                  {saving ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      Save Interests
                    </>
                  )}
                </button>
              </div>
            )}

            {saveSuccess && (
              <div className="mt-3 bg-green/10 border border-green text-green-dark text-sm rounded-xl px-4 py-3 flex items-center gap-2">
                <Check size={14} />
                Interests updated!
              </div>
            )}
          </div>

          {/* Logout */}
          <div className="px-1">
            <button
              onClick={handleLogout}
              className="w-full py-3.5 rounded-xl border-2 border-gray-mid text-gray-dark font-semibold text-sm flex items-center justify-center gap-2 hover:border-red-300 hover:text-red-500 transition-colors"
            >
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        </main>

        <BottomNav active="profile" />
      </div>
    </div>
  )
}
