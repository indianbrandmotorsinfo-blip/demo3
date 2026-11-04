import React, { useState } from 'react';
import { Submission, Role, User } from '../types';
import { ExternalLink, CheckCircle, XCircle, Clock, Send, MessageSquare } from 'lucide-react';

interface SubmissionsViewProps {
  submissions: Submission[];
  role: Role;
  currentUser: User;
  onUpdateStatus: (id: string, status: 'APPROVED' | 'REJECTED', notes: string) => void;
  onSubmitNew: (assignmentTitle: string, groupName: string, repoUrl: string, docUrl: string) => void;
}

export const SubmissionsView: React.FC<SubmissionsViewProps> = ({
  submissions,
  role,
  currentUser,
  onUpdateStatus,
  onSubmitNew
}) => {
  const [selectedSub, setSelectedSub] = useState<Submission | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);

  // Submit form state
  const [assignmentTitle, setAssignmentTitle] = useState('PostgreSQL Schema Migration');
  const [groupName, setGroupName] = useState('Data Guardians');
  const [repoUrl, setRepoUrl] = useState('');
  const [docUrl, setDocUrl] = useState('');

  const handleOpenReview = (sub: Submission) => {
    setSelectedSub(sub);
    setReviewNotes(sub.reviewNotes || '');
  };

  const handleSaveReview = (status: 'APPROVED' | 'REJECTED') => {
    if (selectedSub) {
      onUpdateStatus(selectedSub.id, status, reviewNotes);
      setSelectedSub(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl || !docUrl) return;
    onSubmitNew(assignmentTitle, groupName, repoUrl, docUrl);
    setRepoUrl('');
    setDocUrl('');
    setIsSubmitModalOpen(false);
  };

  return (
    <div 
      id="submissions-view-container"
      style={{ 
        padding: 32, 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 24,
        overflowY: 'auto'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
            Project Submissions & Reviews
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            {role === 'admin' 
              ? 'Evaluate student repositories, verify automated test results, and grade deliverables' 
              : 'Turn in your project code repositories, documentation PDFs, and track feedback'}
          </p>
        </div>

        {role === 'student' && (
          <button
            id="btn-turn-in-work"
            onClick={() => setIsSubmitModalOpen(true)}
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
            <Send size={16} />
            <span>Turn In Project</span>
          </button>
        )}
      </div>

      {/* Submissions Table Container */}
      <div className="table-container">
        <div className="table-header">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
            Deliverables Log
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {submissions.length} Total Submissions
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Assignment</th>
                <th>Team / Submitter</th>
                <th>Repository</th>
                <th>Documentation</th>
                <th>Submitted</th>
                <th>Status</th>
                {role === 'admin' && <th style={{ textAlign: 'right' }}>Review</th>}
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub) => {
                let badgeClass = 'badge-open';
                if (sub.status === 'PENDING') badgeClass = 'badge-pending';
                if (sub.status === 'REJECTED') badgeClass = 'badge-full';

                return (
                  <tr key={sub.id} id={`sub-row-${sub.id}`}>
                    <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      {sub.assignmentTitle}
                    </td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{sub.groupName}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>By {sub.submitterName}</div>
                    </td>
                    <td>
                      <a 
                        href={sub.repoUrl} 
                        target="_blank" 
                        rel="noreferrer"
                        style={{ color: 'var(--accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: '0.85rem' }}
                      >
                        <span>GitHub</span>
                        <ExternalLink size={12} />
                      </a>
                    </td>
                    <td>
                      <a 
                        href={sub.docUrl} 
                        target="_blank" 
                        rel="noreferrer"
                        style={{ color: 'var(--accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: '0.85rem' }}
                      >
                        <span>PDF Spec</span>
                        <ExternalLink size={12} />
                      </a>
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {sub.submittedDate}
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>
                        {sub.status}
                      </span>
                    </td>
                    {role === 'admin' && (
                      <td style={{ textAlign: 'right' }}>
                        <button
                          id={`btn-review-${sub.id}`}
                          onClick={() => handleOpenReview(sub)}
                          style={{
                            background: 'transparent',
                            border: '1px solid var(--border)',
                            borderRadius: 6,
                            padding: '6px 12px',
                            fontSize: '0.8rem',
                            color: 'var(--text-main)',
                            cursor: 'pointer'
                          }}
                        >
                          Grade / Audit
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review Modal (Admin) */}
      {selectedSub && (
        <div 
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
              maxWidth: 480,
              padding: 24,
              display: 'flex',
              flexDirection: 'column',
              gap: 20
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: '0 0 4px 0', color: 'var(--text-main)' }}>
                Review Submission
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                {selectedSub.assignmentTitle} &bull; {selectedSub.groupName}
              </p>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                Instructor Feedback & Notes
              </label>
              <textarea
                id="instructor-notes-input"
                rows={4}
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Enter feedback or requirements for revisions..."
                style={{
                  width: '100%',
                  padding: 12,
                  borderRadius: 8,
                  border: '1px solid var(--border)',
                  background: 'var(--bg)',
                  color: 'var(--text-main)',
                  fontSize: '0.875rem',
                  outline: 'none',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                onClick={() => setSelectedSub(null)}
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
                id="btn-reject-sub"
                onClick={() => handleSaveReview('REJECTED')}
                style={{
                  padding: '8px 16px',
                  borderRadius: 6,
                  border: 'none',
                  background: '#ef4444',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Reject / Revise
              </button>
              <button
                id="btn-approve-sub"
                onClick={() => handleSaveReview('APPROVED')}
                style={{
                  padding: '8px 16px',
                  borderRadius: 6,
                  border: 'none',
                  background: '#10b981',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Approve Deliverable
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Turn In Project Modal (Student) */}
      {isSubmitModalOpen && (
        <div 
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
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 12,
              width: '100%',
              maxWidth: 480,
              padding: 24,
              display: 'flex',
              flexDirection: 'column',
              gap: 20
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: '0 0 4px 0', color: 'var(--text-main)' }}>
                Turn In Deliverable
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                Provide your GitHub repository and documentation PDF links
              </p>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                Assignment Title
              </label>
              <input
                type="text"
                value={assignmentTitle}
                onChange={(e) => setAssignmentTitle(e.target.value)}
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

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                Group / Team Name
              </label>
              <input
                type="text"
                value={groupName}
                onChange={(e) => setGroupName(e.target.value)}
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

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                GitHub Repository URL
              </label>
              <input
                type="url"
                required
                placeholder="https://github.com/org/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
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

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                Documentation / Report URL
              </label>
              <input
                type="url"
                required
                placeholder="https://docs.google.com/... or https://..."
                value={docUrl}
                onChange={(e) => setDocUrl(e.target.value)}
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
                onClick={() => setIsSubmitModalOpen(false)}
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
                id="btn-confirm-submit"
                style={{
                  padding: '8px 16px',
                  borderRadius: 6,
                  border: 'none',
                  background: 'var(--accent)',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Submit for Grading
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
