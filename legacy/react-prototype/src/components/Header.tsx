import React from 'react';
import { User, Role } from '../types';
import { ArrowLeftRight } from 'lucide-react';

interface HeaderProps {
  user: User;
  onSwitchRole: (newRole: Role) => void;
  title: string;
}

export const Header: React.FC<HeaderProps> = ({ user, onSwitchRole, title }) => {
  return (
    <header 
      id="portal-header"
      style={{
        height: 72,
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        flexShrink: 0
      }}
    >
      <div className="header-title">
        <h1 
          id="header-heading"
          style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            margin: 0,
            color: 'var(--text-main)',
            letterSpacing: '-0.01em'
          }}
        >
          {title}
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Role Switcher Button */}
        <button
          id="switch-role-btn"
          onClick={() => onSwitchRole(user.role === 'admin' ? 'student' : 'admin')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '6px 12px',
            borderRadius: 6,
            border: '1px solid var(--border)',
            background: 'transparent',
            color: 'var(--text-muted)',
            fontSize: '0.8rem',
            fontWeight: 500,
            cursor: 'pointer'
          }}
          title="Switch view to test both perspectives"
        >
          <ArrowLeftRight size={14} />
          <span>Switch to {user.role === 'admin' ? 'Student' : 'Admin'}</span>
        </button>

        {/* Clean Minimalism User Pill */}
        <div id="user-pill-card" className="user-pill">
          <div className="avatar">
            {user.name.charAt(0)}
          </div>
          <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>
            {user.name} ({user.role === 'admin' ? 'Admin' : 'Student'})
          </span>
        </div>
      </div>
    </header>
  );
};
