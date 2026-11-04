import React, { useState } from 'react';
import { Assignment, AssignmentType } from '../types';
import { X } from 'lucide-react';

interface CreateAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (newAssignment: Omit<Assignment, 'id' | 'currentMembersCount' | 'submissionsCount' | 'groupCount' | 'createdDate'>) => void;
}

export const CreateAssignmentModal: React.FC<CreateAssignmentModalProps> = ({
  isOpen,
  onClose,
  onCreate
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState<AssignmentType>('Group');
  const [maxGroupSize, setMaxGroupSize] = useState(3);
  const [deadline, setDeadline] = useState('2026-10-15');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) return;

    onCreate({
      title,
      description,
      type,
      maxGroupSize: type === 'Individual' ? 1 : Number(maxGroupSize),
      totalCapacity: type === 'Individual' ? 1 : Number(maxGroupSize),
      status: 'OPEN',
      deadline
    });

    setTitle('');
    setDescription('');
    onClose();
  };

  return (
    <div 
      id="create-assignment-modal-backdrop"
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
      <form 
        onSubmit={handleSubmit}
        id="create-assignment-form"
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          width: '100%',
          maxWidth: 500,
          padding: 28,
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
              Create New Assignment
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Publish an assignment with group capacity limits and deadline
            </p>
          </div>
          <button
            type="button"
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

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
            Assignment Title
          </label>
          <input
            id="input-assignment-title"
            type="text"
            required
            placeholder="e.g. Microservices Service Mesh with Istio"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              borderRadius: 8,
              border: '1px solid var(--border)',
              background: 'var(--bg)',
              color: 'var(--text-main)',
              fontSize: '0.875rem'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
            Description & Specifications
          </label>
          <textarea
            id="input-assignment-description"
            rows={3}
            placeholder="Outline objectives, tech stack requirements, and grading criteria..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              borderRadius: 8,
              border: '1px solid var(--border)',
              background: 'var(--bg)',
              color: 'var(--text-main)',
              fontSize: '0.875rem',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
              Assignment Type
            </label>
            <select
              id="select-assignment-type"
              value={type}
              onChange={(e) => setType(e.target.value as AssignmentType)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'var(--bg)',
                color: 'var(--text-main)',
                fontSize: '0.875rem'
              }}
            >
              <option value="Group">Group Project</option>
              <option value="Individual">Individual Work</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
              Max Group Size
            </label>
            <input
              id="input-group-size"
              type="number"
              min={1}
              max={10}
              disabled={type === 'Individual'}
              value={type === 'Individual' ? 1 : maxGroupSize}
              onChange={(e) => setMaxGroupSize(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: type === 'Individual' ? 'var(--border)' : 'var(--bg)',
                color: 'var(--text-main)',
                fontSize: '0.875rem'
              }}
            />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
            Submission Deadline
          </label>
          <input
            id="input-deadline"
            type="date"
            required
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: 8,
              border: '1px solid var(--border)',
              background: 'var(--bg)',
              color: 'var(--text-main)',
              fontSize: '0.875rem'
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 8 }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '8px 16px',
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: 'transparent',
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            id="btn-confirm-create-assignment"
            style={{
              padding: '8px 18px',
              borderRadius: 6,
              border: 'none',
              background: 'var(--accent)',
              color: '#ffffff',
              fontSize: '0.85rem',
              fontWeight: 500,
              cursor: 'pointer'
            }}
          >
            Create Assignment
          </button>
        </div>
      </form>
    </div>
  );
};
