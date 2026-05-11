import React, { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Home, Play, User, RefreshCw, AlertCircle } from 'lucide-react'
import useAppStore from '../store/appStore'
import { api } from '../api/client'
import SnippetCard from '../components/SnippetCard'
import MiniPlayer from '../components/MiniPlayer'
import { useAudioPlayer } from '../hooks/useAudioPlayer'

function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl p-4 border border-gray-mid">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-5 w-16 rounded-full skeleton" />
        <div className="h-5 w-12 rounded-full skeleton" />
      </div>
      <div className="h-4 w-full rounded-lg skeleton mb-2" />
      <div className="h-4 w-3/4 rounded-lg skeleton mb-4" />
      <div className="flex items-center justify-between">
        <div className="h-3 w-24 rounded skeleton" />
        <div className="h-9 w-9 rounded-full skeleton" />
      </div>
    </div>
  )
}

function BottomNav({ active }) {
  const navigate = useNavigate()

  const tabs = [
    { id: 'feed', label: 'Feed', Icon: Home, path: '/feed' },
    { id: 'player', label: 'Player', Icon: Play, path: '/player' },
    { id: 'profile', label: 'Profile', Icon: User, path: '/profile' },
  ]

  return (
    <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[480px] bg-white border-t border-gray-mid z-50">
      <div className="flex items-center">
        {tabs.map(({ id, label, Icon, path }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => navigate(path)}
              className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-colors ${
                isActive ? 'text-blue' : 'text-gray-dark hover:text-navy'
              }`}
            >
              <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-[10px] font-semibold">{label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}

export { BottomNav }

export default function Feed() {
  const navigate = useNavigate()
  const {
    user,
    feed,
    setFeed,
    currentIndex,
    setCurrentIndex,
    isPlaying,
    setIsPlaying,
    nextSnippet,
    prevSnippet,
    getCurrentSnippet,
  } = useAppStore()

  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState(null)
  const interactedRef = useRef(new Set())

  const currentSnippet = getCurrentSnippet()
  const audioUrl = currentSnippet ? api.getAudioUrl(currentSnippet.id) : null

  const handleEnded = useCallback(async () => {
    if (currentSnippet && user && !interactedRef.current.has(`${currentSnippet.id}-completed`)) {
      interactedRef.current.add(`${currentSnippet.id}-completed`)
      try {
        await api.recordInteraction(user.id, currentSnippet.id, 'completed')
      } catch {}
    }
    nextSnippet()
  }, [currentSnippet, user, nextSnippet])

  const handlePlay = useCallback(async () => {
    if (currentSnippet && user && !interactedRef.current.has(`${currentSnippet.id}-played`)) {
      interactedRef.current.add(`${currentSnippet.id}-played`)
      try {
        await api.recordInteraction(user.id, currentSnippet.id, 'played')
      } catch {}
    }
  }, [currentSnippet, user])

  const audioPlayer = useAudioPlayer(audioUrl, {
    onEnded: handleEnded,
    onPlay: handlePlay,
  })

  // Sync playing state to store
  useEffect(() => {
    setIsPlaying(audioPlayer.isPlaying)
  }, [audioPlayer.isPlaying, setIsPlaying])

  const loadFeed = useCallback(async () => {
    if (!user) return
    setLoading(true)
    setError(null)
    try {
      const data = await api.getFeed(user.id)
      const snippets = data?.snippets || []
      setFeed(snippets)
    } catch (err) {
      setError(err.message || 'Failed to load feed')
    } finally {
      setLoading(false)
    }
  }, [user, setFeed])

  useEffect(() => {
    if (feed.length === 0) {
      loadFeed()
    }
  }, [])

  const handleCardPlay = (index) => {
    if (index === currentIndex) {
      audioPlayer.toggle()
    } else {
      setCurrentIndex(index)
      // Audio will reload via useAudioPlayer when audioUrl changes
      // Small delay to let state settle
      setTimeout(() => {
        audioPlayer.play()
      }, 100)
    }
    navigate('/player')
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="min-h-screen bg-gray-light flex flex-col">
      <div className="w-full max-w-[480px] mx-auto flex flex-col min-h-screen">

        {/* Header */}
        <header className="bg-white border-b border-gray-mid px-4 pt-12 pb-4 sticky top-0 z-30">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-black text-blue tracking-tight">PACE</h1>

            <button
              onClick={() => navigate('/profile')}
              className="w-9 h-9 rounded-full bg-navy flex items-center justify-center text-white font-bold text-sm hover:bg-navy-light transition-colors"
              aria-label="Profile"
            >
              {user?.name ? user.name[0].toUpperCase() : 'U'}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 px-4 pb-36 pt-5">
          {/* Feed heading */}
          <div className="mb-5">
            <h2 className="text-lg font-black text-navy">For You</h2>
            <p className="text-xs text-gray-dark mt-0.5">
              <span className="font-semibold text-blue">Daily Mix</span> · {today}
            </p>
          </div>

          {/* Loading skeletons */}
          {loading && (
            <div className="flex flex-col gap-3">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
              <div className="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center">
                <AlertCircle size={28} className="text-red-400" />
              </div>
              <div>
                <p className="font-semibold text-navy mb-1">Couldn't load feed</p>
                <p className="text-sm text-gray-dark">{error}</p>
              </div>
              <button
                onClick={loadFeed}
                className="flex items-center gap-2 bg-blue text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-600 transition-colors"
              >
                <RefreshCw size={14} />
                Try again
              </button>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && feed.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
              <div className="text-4xl">🎧</div>
              <div>
                <p className="font-semibold text-navy mb-1">No snippets yet</p>
                <p className="text-sm text-gray-dark">Check back soon — we're curating your feed.</p>
              </div>
              <button
                onClick={loadFeed}
                className="flex items-center gap-2 bg-blue text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-600 transition-colors"
              >
                <RefreshCw size={14} />
                Refresh
              </button>
            </div>
          )}

          {/* Feed list */}
          {!loading && feed.length > 0 && (
            <div className="flex flex-col gap-3">
              {feed.map((snippet, index) => (
                <div key={snippet.id || index} className="fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
                  <SnippetCard
                    snippet={snippet}
                    isActive={index === currentIndex}
                    isPlaying={index === currentIndex && isPlaying}
                    onPlay={() => handleCardPlay(index)}
                  />
                </div>
              ))}
            </div>
          )}
        </main>

        {/* Mini Player */}
        {feed.length > 0 && currentSnippet && (
          <MiniPlayer
            isPlaying={audioPlayer.isPlaying}
            currentTime={audioPlayer.currentTime}
            duration={audioPlayer.duration}
            progress={audioPlayer.progress}
            onPlayPause={audioPlayer.toggle}
            onNext={() => {
              nextSnippet()
            }}
            onPrev={() => {
              prevSnippet()
            }}
          />
        )}

        {/* Bottom nav */}
        <BottomNav active="feed" />
      </div>
    </div>
  )
}
