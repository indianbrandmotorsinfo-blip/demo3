export type Role = 'admin' | 'student';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  studentId?: string;
}

export type AssignmentType = 'Group' | 'Individual';
export type AssignmentStatus = 'OPEN' | 'FULL' | 'CLOSED';

export interface Assignment {
  id: string;
  title: string;
  description: string;
  type: AssignmentType;
  maxGroupSize: number;
  currentMembersCount: number;
  totalCapacity: number;
  status: AssignmentStatus;
  deadline: string;
  submissionsCount: number;
  groupCount: number;
  createdDate: string;
}

export interface GroupMember {
  studentId: string;
  name: string;
  email: string;
  joinedAt: string;
}

export interface Group {
  id: string;
  assignmentId: string;
  assignmentTitle: string;
  name: string;
  maxSize: number;
  members: GroupMember[];
  isLocked: boolean;
  submissionStatus: 'Not Submitted' | 'Pending Review' | 'Approved' | 'Changes Requested';
  submissionRepo?: string;
  submissionDoc?: string;
  submittedAt?: string;
}

export interface Submission {
  id: string;
  assignmentTitle: string;
  groupName: string;
  submitterName: string;
  repoUrl: string;
  docUrl: string;
  submittedDate: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  reviewNotes?: string;
}
