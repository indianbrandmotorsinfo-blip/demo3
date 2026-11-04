import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { AssignmentsView } from './components/AssignmentsView';
import { GroupsView } from './components/GroupsView';
import { SubmissionsView } from './components/SubmissionsView';
import { AnalyticsView } from './components/AnalyticsView';
import { CreateAssignmentModal } from './components/CreateAssignmentModal';
import { AssignmentDetailModal } from './components/AssignmentDetailModal';
import { 
  INITIAL_ASSIGNMENTS, 
  INITIAL_GROUPS, 
  INITIAL_SUBMISSIONS, 
  CURRENT_ADMIN, 
  CURRENT_STUDENT 
} from './data';
import { Assignment, Group, Role, Submission } from './types';

export default function App() {
  const [role, setRole] = useState<Role>('admin');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [darkMode, setDarkMode] = useState<boolean>(false);

  const [assignments, setAssignments] = useState<Assignment[]>(INITIAL_ASSIGNMENTS);
  const [groups, setGroups] = useState<Group[]>(INITIAL_GROUPS);
  const [submissions, setSubmissions] = useState<Submission[]>(INITIAL_SUBMISSIONS);

  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);

  const currentUser = role === 'admin' ? CURRENT_ADMIN : CURRENT_STUDENT;

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleSwitchRole = (newRole: Role) => {
    setRole(newRole);
  };

  // Create Assignment (Admin)
  const handleCreateAssignment = (
    newAsgData: Omit<Assignment, 'id' | 'currentMembersCount' | 'submissionsCount' | 'groupCount' | 'createdDate'>
  ) => {
    const newAsg: Assignment = {
      ...newAsgData,
      id: `asg-${Date.now()}`,
      currentMembersCount: 0,
      submissionsCount: 0,
      groupCount: 0,
      createdDate: new Date().toISOString().split('T')[0]
    };
    setAssignments([newAsg, ...assignments]);
  };

  // Join Group (Student)
  const handleJoinGroup = (groupId: string) => {
    setGroups((prev) =>
      prev.map((grp) => {
        if (grp.id === groupId) {
          const alreadyIn = grp.members.some((m) => m.email === currentUser.email);
          if (alreadyIn || grp.members.length >= grp.maxSize || grp.isLocked) return grp;

          const updatedMembers = [
            ...grp.members,
            {
              studentId: currentUser.studentId || `CS-${Math.floor(1000 + Math.random() * 9000)}`,
              name: currentUser.name,
              email: currentUser.email,
              joinedAt: new Date().toISOString().split('T')[0]
            }
          ];

          // Also update assignment member count
          setAssignments((asgList) =>
            asgList.map((a) => {
              if (a.id === grp.assignmentId) {
                const newCount = a.currentMembersCount + 1;
                return {
                  ...a,
                  currentMembersCount: newCount,
                  status: newCount >= a.maxGroupSize ? 'FULL' : 'OPEN'
                };
              }
              return a;
            })
          );

          return {
            ...grp,
            members: updatedMembers,
            isLocked: updatedMembers.length >= grp.maxSize
          };
        }
        return grp;
      })
    );
  };

  // Create Group for Assignment (Student)
  const handleCreateGroup = (assignmentId: string, groupName: string) => {
    const targetAsg = assignments.find((a) => a.id === assignmentId);
    if (!targetAsg) return;

    const newGroup: Group = {
      id: `grp-${Date.now()}`,
      assignmentId,
      assignmentTitle: targetAsg.title,
      name: groupName,
      maxSize: targetAsg.maxGroupSize,
      isLocked: false,
      submissionStatus: 'Not Submitted',
      members: [
        {
          studentId: currentUser.studentId || 'CS-8891',
          name: currentUser.name,
          email: currentUser.email,
          joinedAt: new Date().toISOString().split('T')[0]
        }
      ]
    };

    setGroups([...groups, newGroup]);

    // Update assignment counts
    setAssignments((asgs) =>
      asgs.map((a) => {
        if (a.id === assignmentId) {
          const newCount = a.currentMembersCount + 1;
          return {
            ...a,
            groupCount: a.groupCount + 1,
            currentMembersCount: newCount,
            status: newCount >= a.maxGroupSize ? 'FULL' : 'OPEN'
          };
        }
        return a;
      })
    );
  };

  // Toggle Group Lock (Admin)
  const handleToggleLock = (groupId: string) => {
    setGroups((prev) =>
      prev.map((g) => (g.id === groupId ? { ...g, isLocked: !g.isLocked } : g))
    );
  };

  // Review deliverable (Admin)
  const handleUpdateSubmissionStatus = (
    id: string,
    status: 'APPROVED' | 'REJECTED',
    notes: string
  ) => {
    setSubmissions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status, reviewNotes: notes } : s))
    );
  };

  // Turn in work (Student)
  const handleSubmitNew = (
    assignmentTitle: string,
    groupName: string,
    repoUrl: string,
    docUrl: string
  ) => {
    const newSub: Submission = {
      id: `sub-${Date.now()}`,
      assignmentTitle,
      groupName,
      submitterName: currentUser.name,
      repoUrl,
      docUrl,
      submittedDate: new Date().toISOString().split('T')[0],
      status: 'PENDING',
      reviewNotes: 'Awaiting evaluation by course instructor.'
    };
    setSubmissions([newSub, ...submissions]);

    // Update group submission status
    setGroups((prev) =>
      prev.map((g) =>
        g.name === groupName
          ? {
              ...g,
              submissionStatus: 'Pending Review',
              submissionRepo: repoUrl,
              submissionDoc: docUrl,
              submittedAt: new Date().toISOString().split('T')[0]
            }
          : g
      )
    );
  };

  const getHeaderTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return role === 'admin' ? 'Admin Overview' : 'Student Overview';
      case 'assignments':
        return 'Assignment Catalog';
      case 'groups':
        return 'Project Teams & Roster';
      case 'submissions':
        return 'Deliverables & Grading';
      case 'analytics':
        return 'Analytics & Telemetry';
      default:
        return 'Overview';
    }
  };

  return (
    <div 
      id="portal-app-layout"
      style={{
        display: 'flex',
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
        backgroundColor: 'var(--bg)',
        color: 'var(--text-main)'
      }}
    >
      {/* Clean Minimalism Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        role={role}
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
      />

      {/* Main Content Area */}
      <main 
        id="portal-main-area"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          overflow: 'hidden'
        }}
      >
        <Header
          user={currentUser}
          onSwitchRole={handleSwitchRole}
          title={getHeaderTitle()}
        />

        {activeTab === 'dashboard' && (
          <DashboardView
            assignments={assignments}
            role={role}
            onOpenCreateModal={() => setIsCreateModalOpen(true)}
            onSelectAssignment={(asg) => setSelectedAssignment(asg)}
          />
        )}

        {activeTab === 'assignments' && (
          <AssignmentsView
            assignments={assignments}
            role={role}
            onOpenCreateModal={() => setIsCreateModalOpen(true)}
            onSelectAssignment={(asg) => setSelectedAssignment(asg)}
          />
        )}

        {activeTab === 'groups' && (
          <GroupsView
            groups={groups}
            role={role}
            currentUser={currentUser}
            onJoinGroup={handleJoinGroup}
            onToggleLock={handleToggleLock}
          />
        )}

        {activeTab === 'submissions' && (
          <SubmissionsView
            submissions={submissions}
            role={role}
            currentUser={currentUser}
            onUpdateStatus={handleUpdateSubmissionStatus}
            onSubmitNew={handleSubmitNew}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsView
            assignments={assignments}
            groups={groups}
            submissions={submissions}
            role={role}
          />
        )}
      </main>

      {/* Modals */}
      <CreateAssignmentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreateAssignment}
      />

      <AssignmentDetailModal
        assignment={selectedAssignment}
        groups={groups}
        role={role}
        currentUser={currentUser}
        onClose={() => setSelectedAssignment(null)}
        onJoinGroup={handleJoinGroup}
        onCreateGroup={handleCreateGroup}
      />
    </div>
  );
}
