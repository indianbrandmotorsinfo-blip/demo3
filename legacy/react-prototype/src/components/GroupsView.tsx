import React, { useState } from 'react';
import { Group, Role, User } from '../types';
import { Users, Lock, Unlock, CheckCircle, Clock, Plus, ExternalLink } from 'lucide-react';

interface GroupsViewProps {
  groups: Group[];
  role: Role;
  currentUser: User;
  onJoinGroup: (groupId: string) => void;
  onToggleLock: (groupId: string) => void;
}

export const GroupsView: React.FC<GroupsViewProps> = ({
  groups,
  role,
  currentUser,
  onJoinGroup,
  onToggleLock
}) => {
  return (
    <div 
      id="groups-view-container"
      style={{ 
        padding: 32, 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 24,
        overflowY: 'auto'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
            Active Project Groups
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            {role === 'admin' 
              ? 'Oversee group formation, team size caps, and locked submission readiness' 
              : 'Form or join collaborative project teams with your classmates'}
          </p>
        </div>
      </div>

      <div 
        id="groups-grid-list"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: 20
        }}
      >
        {groups.map((group) => {
          const isMember = group.members.some((m) => m.email === currentUser.email);
          const isFull = group.members.length >= group.maxSize;

          let statusBadge = (
            <span className="badge badge-open">
              <CheckCircle size={12} /> Forming
            </span>
          );
          if (group.isLocked || isFull) {
            statusBadge = (
              <span className="badge badge-full">
                <Lock size={12} /> Locked Full
              </span>
            );
          }

          return (
            <div
              key={group.id}
              id={`group-card-${group.id}`}
              style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 12,
                padding: 24,
                display: 'flex',
                flexDirection: 'column',
                gap: 16
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 4px 0', color: 'var(--text-main)' }}>
                    {group.name}
                  </h3>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {group.assignmentTitle}
                  </div>
                </div>
                {statusBadge}
              </div>

              {/* Members List */}
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.05em' }}>
                  Roster ({group.members.length}/{group.maxSize})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {group.members.map((member) => (
                    <div 
                      key={member.studentId}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        fontSize: '0.85rem',
                        padding: '4px 0'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div className="avatar" style={{ width: 22, height: 22, fontSize: '0.7rem' }}>
                          {member.name.charAt(0)}
                        </div>
                        <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{member.name}</span>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                        {member.studentId}
                      </span>
                    </div>
                  ))}

                  {/* Empty slots placeholders */}
                  {Array.from({ length: Math.max(0, group.maxSize - group.members.length) }).map((_, i) => (
                    <div 
                      key={`empty-${i}`}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 8, 
                        fontSize: '0.8rem', 
                        color: 'var(--text-muted)',
                        padding: '4px 0',
                        opacity: 0.6 
                      }}
                    >
                      <div style={{ width: 22, height: 22, borderRadius: '50%', border: '1px dashed var(--border)' }} />
                      <span>Open Slot Available</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Submission info if exists */}
              {group.submissionRepo && (
                <div 
                  style={{ 
                    padding: '8px 12px', 
                    background: 'var(--bg)', 
                    borderRadius: 6, 
                    border: '1px solid var(--border)',
                    fontSize: '0.75rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 4
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                    <span>Submission Status:</span>
                    <span style={{ fontWeight: 600, color: group.submissionStatus === 'Approved' ? '#10b981' : '#f59e0b' }}>
                      {group.submissionStatus}
                    </span>
                  </div>
                  <a 
                    href={group.submissionRepo} 
                    target="_blank" 
                    rel="noreferrer"
                    style={{ color: 'var(--accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                  >
                    <span>View Repository</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
              )}

              {/* Action Buttons */}
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
                {role === 'admin' ? (
                  <button
                    id={`btn-toggle-lock-${group.id}`}
                    onClick={() => onToggleLock(group.id)}
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
                      cursor: 'pointer'
                    }}
                  >
                    {group.isLocked ? <Unlock size={14} /> : <Lock size={14} />}
                    <span>{group.isLocked ? 'Unlock Group' : 'Lock Roster'}</span>
                  </button>
                ) : (
                  <div>
                    {isMember ? (
                      <span className="badge badge-open">Enrolled Member</span>
                    ) : (
                      <button
                        id={`btn-join-group-${group.id}`}
                        disabled={isFull || group.isLocked}
                        onClick={() => onJoinGroup(group.id)}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6,
                          padding: '6px 14px',
                          borderRadius: 6,
                          border: 'none',
                          background: isFull || group.isLocked ? 'var(--border)' : 'var(--accent)',
                          color: isFull || group.isLocked ? 'var(--text-muted)' : '#ffffff',
                          fontSize: '0.8rem',
                          fontWeight: 500,
                          cursor: isFull || group.isLocked ? 'not-allowed' : 'pointer'
                        }}
                      >
                        <Plus size={14} />
                        <span>Join Team</span>
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
