import React from 'react'
import {
  Cpu, Trophy, Rocket, Heart, Bot,
  Newspaper, Music2, Shield, Film, Tv,
  Globe, Briefcase, TrendingUp, BookOpen,
  Gamepad2, Leaf, FlaskConical, Utensils, MapPin, Brain,
} from 'lucide-react'

const CATEGORY_CONFIG = {
  // ── Frontend show-level interest IDs ────────────────────────────────────
  sports:      { color: '#FF6B35', bg: '#FFF0EB', label: 'Sports',       Icon: Trophy },
  tech:        { color: '#0066FF', bg: '#EBF3FF', label: 'Tech',         Icon: Cpu },
  ai:          { color: '#FF61B6', bg: '#FFE8F5', label: 'AI',           Icon: Bot },
  science:     { color: '#7B61FF', bg: '#F0EEFF', label: 'Science',      Icon: FlaskConical },
  health:      { color: '#00D9A3', bg: '#E6FAF5', label: 'Health',       Icon: Heart },
  news:        { color: '#374151', bg: '#F3F4F6', label: 'News',         Icon: Newspaper },
  pop:         { color: '#EC4899', bg: '#FDF2F8', label: 'Pop Culture',  Icon: Music2 },
  crime:       { color: '#DC2626', bg: '#FEF2F2', label: 'True Crime',   Icon: Shield },
  // ── Backend category IDs (snippet pills) ────────────────────────────────
  nba:         { color: '#FF6B35', bg: '#FFF0EB', label: 'NBA',          Icon: Trophy },
  nfl:         { color: '#FF6B35', bg: '#FFF0EB', label: 'NFL',          Icon: Trophy },
  soccer:      { color: '#FF6B35', bg: '#FFF0EB', label: 'Soccer',       Icon: Trophy },
  mlb:         { color: '#FF6B35', bg: '#FFF0EB', label: 'MLB',          Icon: Trophy },
  startups:    { color: '#0066FF', bg: '#EBF3FF', label: 'Startups',     Icon: Cpu },
  gadgets:     { color: '#0066FF', bg: '#EBF3FF', label: 'Gadgets',      Icon: Cpu },
  gaming:      { color: '#0066FF', bg: '#EBF3FF', label: 'Gaming',       Icon: Gamepad2 },
  space:       { color: '#7B61FF', bg: '#F0EEFF', label: 'Space',        Icon: Rocket },
  climate:     { color: '#10B981', bg: '#ECFDF5', label: 'Climate',      Icon: Leaf },
  movies:      { color: '#EC4899', bg: '#FDF2F8', label: 'Movies',       Icon: Film },
  tv:          { color: '#EC4899', bg: '#FDF2F8', label: 'TV',           Icon: Tv },
  music:       { color: '#EC4899', bg: '#FDF2F8', label: 'Music',        Icon: Music2 },
  us_politics: { color: '#374151', bg: '#F3F4F6', label: 'Politics',     Icon: Newspaper },
  world_news:  { color: '#374151', bg: '#F3F4F6', label: 'World News',   Icon: Globe },
  business:    { color: '#374151', bg: '#F3F4F6', label: 'Business',     Icon: Briefcase },
  markets:     { color: '#374151', bg: '#F3F4F6', label: 'Markets',      Icon: TrendingUp },
  true_crime:  { color: '#DC2626', bg: '#FEF2F2', label: 'True Crime',   Icon: Shield },
  history:     { color: '#92400E', bg: '#FFFBEB', label: 'History',      Icon: BookOpen },
  psychology:  { color: '#00D9A3', bg: '#E6FAF5', label: 'Psychology',   Icon: Brain },
  food:        { color: '#00D9A3', bg: '#E6FAF5', label: 'Food',         Icon: Utensils },
  travel:      { color: '#00D9A3', bg: '#E6FAF5', label: 'Travel',       Icon: MapPin },
}

const DEFAULT_CONFIG = {
  color: '#6B7280',
  bg: '#F3F4F6',
  label: 'Other',
  Icon: Cpu,
}

export default function CategoryPill({ category, size = 'md', dark = false }) {
  const config = CATEGORY_CONFIG[category?.toLowerCase()] || DEFAULT_CONFIG
  const { color, bg, label, Icon } = config

  if (size === 'sm') {
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
        style={{
          color: dark ? '#ffffff' : color,
          backgroundColor: dark ? `${color}33` : bg,
        }}
      >
        <Icon size={10} />
        {label}
      </span>
    )
  }

  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold"
      style={{
        color: dark ? '#ffffff' : color,
        backgroundColor: dark ? `${color}33` : bg,
      }}
    >
      <Icon size={13} />
      {label}
    </span>
  )
}

export { CATEGORY_CONFIG, DEFAULT_CONFIG }
