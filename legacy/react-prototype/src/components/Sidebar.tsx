import React from 'react';
import { 
  LayoutDashboard, 
  BookOpen, 
  Users, 
  FileCheck2, 
  BarChart3, 
  HelpCircle, 
  Sun, 
  Moon,
  Network
} from 'lucide-react';
import { Role } from '../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  role: Role;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  role,
  darkMode,
  toggleDarkMode
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'assignments', label: 'Assignments', icon: BookOpen },
    { id: 'groups', label: 'Groups', icon: Users },
    { id: 'submissions', label: 'Submissions', icon: FileCheck2 },
    { id: 'analytics', label: role === 'admin' ? 'Group Analytics' : 'My Progress', icon: BarChart3 },
  ];

  return (
    <aside 
      id="portal-sidebar" 
      style={{
        width: 240,
        background: 'var(--sidebar)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: 24,
        flexShrink: 0
      }}
    >
      {/* Clean Minimalism Logo */}
      <div 
        id="portal-logo"
        style={{
          fontWeight: 700,
          fontSize: '1.25rem',
          color: 'var(--accent)',
          marginBottom: 36,
          display: 'flex',
          alignItems: 'center',
          gap: 10
        }}
      >
        <div 
          style={{
            width: 32,
            height: 32,
            background: 'var(--accent)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff'
          }}
        >
          <Network size={18} strokeWidth={2.4} />
        </div>
        <span style={{ color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
          Portal<span style={{ color: 'var(--accent)' }}>.</span>
        </span>
      </div>

      {/* Navigation Links */}
      <nav id="sidebar-nav" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              id={`nav-link-${item.id}`}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 14px',
                borderRadius: 8,
                color: isActive ? 'var(--accent)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--accent-light)' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent)' : 'var(--text-muted)'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Bottom Documentation & Theme Toggle */}
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <button
          id="toggle-dark-mode"
          onClick={toggleDarkMode}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 14px',
            borderRadius: 8,
            color: 'var(--text-muted)',
            backgroundColor: 'transparent',
            fontSize: '0.85rem',
            border: 'none',
            cursor: 'pointer',
            textAlign: 'left',
            width: '100%'
          }}
        >
          {darkMode ? <Sun size={17} /> : <Moon size={17} />}
          <span>{darkMode ? 'Light Theme' : 'Dark Theme'}</span>
        </button>

        <a
          href="#docs"
          id="nav-docs-link"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 14px',
            borderRadius: 8,
            color: 'var(--text-muted)',
            fontSize: '0.85rem',
            textDecoration: 'none'
          }}
          onClick={(e) => e.preventDefault()}
        >
          <HelpCircle size={17} />
          <span>Documentation</span>
        </a>
      </div>
    </aside>
  );
};
