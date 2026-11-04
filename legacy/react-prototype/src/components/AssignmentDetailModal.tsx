import React, { useState } from 'react';
import { Assignment, Group, Role, User } from '../types';
import { X, Users, Calendar, Plus, Lock, CheckCircle } from 'lucide-react';

interface AssignmentDetailModalProps {
  assignment: Assignment | null;
  groups: Group[];
  role: Role;
  currentUser: User;
  onClose: () => void;
  onJoinGroup: (groupId: string) => void;
  onCreateGroup: (assignmentId: string, groupName: string) => void;
}

export const AssignmentDetailModal: React.FC<AssignmentDetailModalProps> = ({
  assignment,
  groups,
  role,
  currentUser,
  onClose,
  onJoinGroup,
  onCreateGroup
}) => {
  const [newGroupName, setNewGroupName] = useState('');
  const [isCreatingGroup, setIsCreatingGroup] = useState(false);

  if (!assignment) return null;

  const assignmentGroups = groups.filter((g) => g.assignmentId === assignment.id);
  const isEnrolledInAny = assignmentGroups.some((g) =>
    g.members.some((m) => m.email === currentUser.email)
  );

  const handleCreateGroupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;
    onCreateGroup(assignment.id, newGroupName.trim());
    setNewGroupName('');
    setIsCreatingGroup(false);
  };

  return (
    <div 
      id="assignment-detail-backdrop"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(15, 23, 42, 0.4)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 16
      }}
    >
      <div 
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          width: '100%',
          maxWidth: 600,
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.05)'
        }}
      >
        {/* Modal Header */}
        <div style={{ padding: '24px 28px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <span className={assignment.type === 'Group' ? 'badge badge-group' : 'badge badge-neutral'}>
                {assignment.type}
              </span>
              <span className={`badge ${assignment.status === 'OPEN' ? 'badge-open' : assignment.status === 'FULL' ? 'badge-full' : 'badge-pending'}`}>
                {assignment.status}
              </span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
              {assignment.title}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 6 }}>
              <Calendar size={14} />
              <span>Deadline: {assignment.deadline}</span>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: 4
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px 28px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
              Assignment Overview
            </h4>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.6, margin: 0 }}>
              {assignment.description}
            </p>
          </div>

          {/* Group Roster section */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', margin: 0, letterSpacing: '0.05em' }}>
                Teams Formed ({assignmentGroups.length})
              </h4>

              {role === 'student' && !isEnrolledInAny && assignment.status === 'OPEN' && (
                <button
                  id="btn-show-create-group"
                  onClick={() => setIsCreatingGroup(!isCreatingGroup)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 6,
                    border: '1px solid var(--border)',
                    background: 'var(--bg)',
                    color: 'var(--accent)',
                    fontSize: '0.8rem',
                    cursor: 'pointer'
                  }}
                >
                  <Plus size={14} />
                  <span>Form New Team</span>
                </button>
              )}
            </div>

            {/* Inline Form New Team */}
            {isCreatingGroup && (
              <form onSubmit={handleCreateGroupSubmit} style={{ marginBottom: 16, padding: 14, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', gap: 8 }}>
                <input
                  type="text"
                  required
                  placeholder="Enter team name (e.g. Distributed Pioneers)..."
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    borderRadius: 6,
                    border: '1px solid var(--border)',
                    background: 'var(--surface)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem'
                  }}
                />
                <button
                  type="submit"
                  style={{
                    padding: '8px 14px',
                    borderRadius: 6,
                    border: 'none',
                    background: 'var(--accent)',
                    color: '#ffffff',
                    fontSize: '0.85rem',
                    fontWeight: 500,
                    cursor: 'pointer'
                  }}
                >
                  Create
                </button>
              </form>
            )}

            {assignmentGroups.length === 0 ? (
              <div style={{ padding: 20, textAlign: 'center', background: 'var(--bg)', borderRadius: 8, color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No teams formed yet for this assignment. Be the first to start a group!
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {assignmentGroups.map((grp) => {
                  const isMember = grp.members.some((m) => m.email === currentUser.email);
                  const isFull = grp.members.length >= grp.maxSize;

                  return (
                    <div
                      key={grp.id}
                      style={{
                        padding: 14,
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                          {grp.name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          {grp.members.length} / {grp.maxSize} members &bull; {grp.members.map((m) => m.name).join(', ')}
                        </div>
                      </div>

                      {role === 'student' && (
                        <div>
                          {isMember ? (
                            <span className="badge badge-open">Joined</span>
                          ) : (
                            <button
                              disabled={isFull || grp.isLocked}
                              onClick={() => onJoinGroup(grp.id)}
                              style={{
                                padding: '6px 12px',
                                borderRadius: 6,
                                border: 'none',
                                background: isFull || grp.isLocked ? 'var(--border)' : 'var(--accent)',
                                color: isFull || grp.isLocked ? 'var(--text-muted)' : '#ffffff',
                                fontSize: '0.8rem',
                                cursor: isFull || grp.isLocked ? 'not-allowed' : 'pointer'
                              }}
                            >
                              Join
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{ padding: '16px 28px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 18px',
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: 'transparent',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
