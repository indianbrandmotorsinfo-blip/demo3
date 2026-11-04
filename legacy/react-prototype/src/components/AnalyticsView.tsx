import React from 'react';
import { Assignment, Group, Submission, Role } from '../types';
import { BarChart3, CheckCircle2, AlertCircle, PieChart, Users2 } from 'lucide-react';

interface AnalyticsViewProps {
  assignments: Assignment[];
  groups: Group[];
  submissions: Submission[];
  role: Role;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  assignments,
  groups,
  submissions,
  role
}) => {
  const totalAssignments = assignments.length;
  const openCount = assignments.filter((a) => a.status === 'OPEN').length;
  const fullCount = assignments.filter((a) => a.status === 'FULL').length;
  const closedCount = assignments.filter((a) => a.status === 'CLOSED').length;

  const approvedSubs = submissions.filter((s) => s.status === 'APPROVED').length;
  const pendingSubs = submissions.filter((s) => s.status === 'PENDING').length;
  const rejectedSubs = submissions.filter((s) => s.status === 'REJECTED').length;

  const openPct = Math.round((openCount / (totalAssignments || 1)) * 100);
  const fullPct = Math.round((fullCount / (totalAssignments || 1)) * 100);
  const closedPct = 100 - openPct - fullPct;

  return (
    <div 
      id="analytics-view-container"
      style={{ 
        padding: 32, 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 24,
        overflowY: 'auto'
      }}
    >
      <div>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
          {role === 'admin' ? 'Cohort Analytics & System Telemetry' : 'Student Learning & Performance'}
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
          Real-time metrics on group distribution, assignment capacity, and deliverable review workflows
        </p>
      </div>

      {/* KPI Cards */}
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 20
        }}
      >
        <div className="stat-card">
          <div className="stat-label">Assignment Capacity</div>
          <div className="stat-value">{fullCount + openCount} Active</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
            {openCount} Accepting Roster Members
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Review Velocity</div>
          <div className="stat-value">{approvedSubs} Approved</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
            {pendingSubs} Awaiting Evaluation
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Formed Teams</div>
          <div className="stat-value">{groups.length} Groups</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
            Across all project tracks
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Database Health</div>
          <div className="stat-value" style={{ color: '#10b981' }}>Optimal</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
            PostgreSQL + Redis Connected
          </div>
        </div>
      </div>

      {/* Analytics Breakdown Containers */}
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20
        }}
      >
        {/* Status Distribution */}
        <div className="table-container" style={{ padding: 24 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 16px 0', color: 'var(--text-main)' }}>
            Assignment Status Distribution
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 6 }}>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Open for Enrollment</span>
                <span style={{ color: 'var(--text-muted)' }}>{openCount} ({openPct}%)</span>
              </div>
              <div style={{ height: 8, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
                <div style={{ width: `${openPct}%`, height: '100%', background: '#10b981', borderRadius: 999 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 6 }}>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Capacity Reached (Full)</span>
                <span style={{ color: 'var(--text-muted)' }}>{fullCount} ({fullPct}%)</span>
              </div>
              <div style={{ height: 8, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
                <div style={{ width: `${fullPct}%`, height: '100%', background: '#ef4444', borderRadius: 999 }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 6 }}>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Past Deadline (Closed)</span>
                <span style={{ color: 'var(--text-muted)' }}>{closedCount} ({closedPct}%)</span>
              </div>
              <div style={{ height: 8, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
                <div style={{ width: `${closedPct}%`, height: '100%', background: '#64748b', borderRadius: 999 }} />
              </div>
            </div>
          </div>
        </div>

        {/* Deliverables Breakdown */}
        <div className="table-container" style={{ padding: 24 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 16px 0', color: 'var(--text-main)' }}>
            Submissions & Review Status
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} />
                <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Approved Submissions</span>
              </div>
              <span className="badge badge-open">{approvedSubs} Passed</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }} />
                <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Pending Review</span>
              </div>
              <span className="badge badge-pending">{pendingSubs} In Queue</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} />
                <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Revisions Requested</span>
              </div>
              <span className="badge badge-full">{rejectedSubs} Need Edits</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
