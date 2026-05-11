import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAppStore = create(
  persist(
    (set, get) => ({
      // User state
      user: null,
      setUser: (user) => set({ user }),
      clearUser: () => set({ user: null }),

      // Feed state
      feed: [],
      setFeed: (feed) => set({ feed, currentIndex: 0 }),
      appendFeed: (snippets) =>
        set((state) => ({ feed: [...state.feed, ...snippets] })),

      // Player state
      currentIndex: 0,
      isPlaying: false,

      setCurrentIndex: (i) => set({ currentIndex: i }),
      setIsPlaying: (bool) => set({ isPlaying: bool }),

      nextSnippet: () =>
        set((state) => {
          const { feed, currentIndex } = state
          if (feed.length === 0) return {}
          const next = (currentIndex + 1) % feed.length
          return { currentIndex: next }
        }),

      prevSnippet: () =>
        set((state) => {
          const { feed, currentIndex } = state
          if (feed.length === 0) return {}
          const prev = (currentIndex - 1 + feed.length) % feed.length
          return { currentIndex: prev }
        }),

      // Selector: current snippet
      getCurrentSnippet: () => {
        const { feed, currentIndex } = get()
        if (feed.length === 0) return null
        return feed[currentIndex] || null
      },
    }),
    {
      name: 'pace-storage',
      partialize: (state) => ({ user: state.user }),
    }
  )
)

export default useAppStore
