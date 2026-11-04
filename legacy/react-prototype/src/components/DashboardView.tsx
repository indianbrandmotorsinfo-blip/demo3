import React from 'react';
import { Assignment, Role } from '../types';
import { Plus, ArrowRight, CheckCircle2 } from 'lucide-react';

interface DashboardViewProps {
  assignments: Assignment[];
  role: Role;
  onOpenCreateModal: () => void;
  onSelectAssignment: (assignment: Assignment) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  assignments,
  role,
  onOpenCreateModal,
  onSelectAssignment
}) => {
  const totalAssignments = assignments.length;
  const openCount = assignments.filter((a) => a.status === 'OPEN').length;
  const fullCount = assignments.filter((a) => a.status === 'FULL').length;

  return (
    <div 
      id="dashboard-content" 
      style={{ 
        padding: 32, 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 24,
        overflowY: 'auto'
      }}
    >
      {/* Clean Minimalism Stats Grid */}
      <div 
        id="stats-metrics-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 20
        }}
      >
        <div id="stat-total-assignments" className="stat-card">
          <div className="stat-label">Total Assignments</div>
          <div className="stat-value">{totalAssignments}</div>
        </div>

        <div id="stat-active-groups" className="stat-card">
          <div className="stat-label">Active Groups</div>
          <div className="stat-value">86</div>
        </div>

        <div id="stat-pending-reviews" className="stat-card">
          <div className="stat-label">Pending Reviews</div>
          <div className="stat-value">12</div>
        </div>

        <div id="stat-server-health" className="stat-card">
          <div className="stat-label">Server Health</div>
          <div className="stat-value" style={{ color: '#10b981' }}>99.9%</div>
        </div>
      </div>

      {/* Clean Minimalism Table Container */}
      <div id="recent-assignments-card" className="table-container">
        <div className="table-header">
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
              Recent Assignments
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
              {role === 'admin' 
                ? 'Manage active courses, group quotas, and submissions' 
                : 'Browse available group and individual course projects'}
            </p>
          </div>

          {role === 'admin' && (
            <button 
              id="create-assignment-btn"
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
              <span>Create Assignment</span>
            </button>
          )}
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table id="assignments-data-table" className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Capacity</th>
                <th>Status</th>
                <th>Submissions</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((item) => {
                let badgeClass = 'badge-open';
                if (item.status === 'FULL') badgeClass = 'badge-full';
                if (item.status === 'CLOSED') badgeClass = 'badge-pending';

                return (
                  <tr key={item.id} id={`assignment-row-${item.id}`}>
                    <td style={{ fontWeight: 500, color: 'var(--text-main)' }}>
                      <div>{item.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        Due {item.deadline}
                      </div>
                    </td>
                    <td>
                      <span className={item.type === 'Group' ? 'badge badge-group' : 'badge badge-neutral'}>
                        {item.type}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {item.currentMembersCount}/{item.maxGroupSize}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>
                        {item.status}
                      </span>
                    </td>
                    <td>{item.submissionsCount}</td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        id={`btn-view-${item.id}`}
                        onClick={() => onSelectAssignment(item)}
                        style={{
                          background: 'transparent',
                          border: '1px solid var(--border)',
                          borderRadius: 6,
                          padding: '6px 12px',
                          fontSize: '0.8rem',
                          color: 'var(--accent)',
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 4
                        }}
                      >
                        <span>Details</span>
                        <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
