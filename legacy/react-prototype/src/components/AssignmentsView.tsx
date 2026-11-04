import React, { useState } from 'react';
import { Assignment, Role } from '../types';
import { Search, Plus, Users, Calendar, ArrowRight, Check } from 'lucide-react';

interface AssignmentsViewProps {
  assignments: Assignment[];
  role: Role;
  onOpenCreateModal: () => void;
  onSelectAssignment: (assignment: Assignment) => void;
}

export const AssignmentsView: React.FC<AssignmentsViewProps> = ({
  assignments,
  role,
  onOpenCreateModal,
  onSelectAssignment
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [filterType, setFilterType] = useState<string>('ALL');

  const filtered = assignments.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'ALL' || item.status === filterStatus;
    const matchesType = filterType === 'ALL' || item.type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div 
      id="assignments-view-container"
      style={{ 
        padding: 32, 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 24,
        overflowY: 'auto'
      }}
    >
      {/* Action Header & Search */}
      <div 
        style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          flexWrap: 'wrap', 
          gap: 16 
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1, minWidth: 260, maxWidth: 460 }}>
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 10, 
              background: 'var(--surface)', 
              border: '1px solid var(--border)', 
              borderRadius: 8, 
              padding: '8px 14px', 
              width: '100%' 
            }}
          >
            <Search size={16} color="var(--text-muted)" />
            <input
              id="assignment-search-input"
              type="text"
              placeholder="Search assignments or topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                border: 'none',
                outline: 'none',
                background: 'transparent',
                fontSize: '0.875rem',
                width: '100%',
                color: 'var(--text-main)'
              }}
            />
          </div>
        </div>

        {role === 'admin' && (
          <button
            id="btn-create-assignment-page"
            onClick={onOpenCreateModal}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '8px 16px',
              borderRadius: 6,
              fontSize: '0.85rem',
              fontWeight: 500,
              background: 'var(--accent)',
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            <Plus size={16} />
            <span>New Assignment</span>
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {['ALL', 'OPEN', 'FULL', 'CLOSED'].map((status) => (
          <button
            key={status}
            id={`filter-status-${status.toLowerCase()}`}
            onClick={() => setFilterStatus(status)}
            style={{
              padding: '6px 14px',
              borderRadius: 999,
              border: '1px solid var(--border)',
              background: filterStatus === status ? 'var(--accent-light)' : 'var(--surface)',
              color: filterStatus === status ? 'var(--accent)' : 'var(--text-muted)',
              fontWeight: filterStatus === status ? 600 : 500,
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {status}
          </button>
        ))}

        <div style={{ width: 1, background: 'var(--border)', margin: '0 4px' }} />

        {['ALL', 'Group', 'Individual'].map((type) => (
          <button
            key={type}
            id={`filter-type-${type.toLowerCase()}`}
            onClick={() => setFilterType(type)}
            style={{
              padding: '6px 14px',
              borderRadius: 999,
              border: '1px solid var(--border)',
              background: filterType === type ? 'var(--accent-light)' : 'var(--surface)',
              color: filterType === type ? 'var(--accent)' : 'var(--text-muted)',
              fontWeight: filterType === type ? 600 : 500,
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {type === 'ALL' ? 'All Types' : type}
          </button>
        ))}
      </div>

      {/* Assignments Grid */}
      <div 
        id="assignments-grid-list"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: 20
        }}
      >
        {filtered.map((asg) => {
          let badgeClass = 'badge-open';
          if (asg.status === 'FULL') badgeClass = 'badge-full';
          if (asg.status === 'CLOSED') badgeClass = 'badge-pending';

          const pct = Math.round((asg.currentMembersCount / asg.maxGroupSize) * 100);

          return (
            <div
              key={asg.id}
              id={`card-assignment-${asg.id}`}
              style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 12,
                padding: 24,
                display: 'flex',
                flexDirection: 'column',
                gap: 16,
                transition: 'border-color 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                <span className={asg.type === 'Group' ? 'badge badge-group' : 'badge badge-neutral'}>
                  {asg.type}
                </span>
                <span className={`badge ${badgeClass}`}>
                  {asg.status}
                </span>
              </div>

              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 6px 0', color: 'var(--text-main)' }}>
                  {asg.title}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                  {asg.description}
                </p>
              </div>

              {/* Progress & Slots */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                  <span>Group Capacity</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                    {asg.currentMembersCount} / {asg.maxGroupSize} Members
                  </span>
                </div>
                <div style={{ height: 6, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${pct}%`, 
                      height: '100%', 
                      background: asg.status === 'FULL' ? '#ef4444' : 'var(--accent)',
                      borderRadius: 999 
                    }} 
                  />
                </div>
              </div>

              <div 
                style={{ 
                  marginTop: 'auto', 
                  paddingTop: 12, 
                  borderTop: '1px solid var(--border)', 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center' 
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <Calendar size={14} />
                  <span>Due {asg.deadline}</span>
                </div>

                <button
                  id={`btn-open-detail-${asg.id}`}
                  onClick={() => onSelectAssignment(asg)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 14px',
                    borderRadius: 6,
                    border: '1px solid var(--border)',
                    background: 'transparent',
                    color: 'var(--accent)',
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    cursor: 'pointer'
                  }}
                >
                  <span>{role === 'admin' ? 'Manage' : 'Join / View'}</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
