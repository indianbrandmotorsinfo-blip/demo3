import { Assignment, Group, Submission, User } from './types';

export const CURRENT_ADMIN: User = {
  id: 'usr-1',
  name: 'Sarah Miller',
  email: 'sarah.miller@university.edu',
  role: 'admin'
};

export const CURRENT_STUDENT: User = {
  id: 'usr-2',
  name: 'Alex Rivera',
  email: 'alex.rivera@student.edu',
  role: 'student',
  studentId: 'CS-2024-8891'
};

export const INITIAL_ASSIGNMENTS: Assignment[] = [
  {
    id: 'asg-1',
    title: 'AWS VPC Infrastructure Design',
    description: 'Design and deploy multi-tier Virtual Private Cloud architecture with public/private subnets and NAT gateway.',
    type: 'Group',
    maxGroupSize: 3,
    currentMembersCount: 3,
    totalCapacity: 3,
    status: 'FULL',
    deadline: '2026-09-18',
    submissionsCount: 12,
    groupCount: 4,
    createdDate: '2026-08-20'
  },
  {
    id: 'asg-2',
    title: 'Redis Cache Optimization',
    description: 'Benchmark Redis caching layer versus raw relational DB queries and implement cache-aside pattern.',
    type: 'Individual',
    maxGroupSize: 1,
    currentMembersCount: 1,
    totalCapacity: 1,
    status: 'FULL',
    deadline: '2026-09-22',
    submissionsCount: 8,
    groupCount: 8,
    createdDate: '2026-08-22'
  },
  {
    id: 'asg-3',
    title: 'PostgreSQL Schema Migration',
    description: 'Implement zero-downtime database migration strategy with rollback scripts and test assertions.',
    type: 'Group',
    maxGroupSize: 4,
    currentMembersCount: 2,
    totalCapacity: 4,
    status: 'OPEN',
    deadline: '2026-09-30',
    submissionsCount: 0,
    groupCount: 2,
    createdDate: '2026-08-25'
  },
  {
    id: 'asg-4',
    title: 'Flask Authentication Module',
    description: 'Build JWT + session token hybrid authentication service with rate limiting and secure HTTP-only cookies.',
    type: 'Individual',
    maxGroupSize: 1,
    currentMembersCount: 0,
    totalCapacity: 1,
    status: 'OPEN',
    deadline: '2026-10-05',
    submissionsCount: 0,
    groupCount: 0,
    createdDate: '2026-08-28'
  },
  {
    id: 'asg-5',
    title: 'Nginx Load Balancer Config',
    description: 'Configure reverse proxy load balancing with health checks, SSL termination, and rate limiting.',
    type: 'Group',
    maxGroupSize: 5,
    currentMembersCount: 3,
    totalCapacity: 5,
    status: 'OPEN',
    deadline: '2026-10-10',
    submissionsCount: 2,
    groupCount: 3,
    createdDate: '2026-08-30'
  },
  {
    id: 'asg-6',
    title: 'Legacy DB Audit Report',
    description: 'Comprehensive audit of relational schema performance, slow queries, index efficiency, and security vectors.',
    type: 'Group',
    maxGroupSize: 4,
    currentMembersCount: 4,
    totalCapacity: 4,
    status: 'CLOSED',
    deadline: '2026-09-01',
    submissionsCount: 4,
    groupCount: 4,
    createdDate: '2026-08-10'
  }
];

export const INITIAL_GROUPS: Group[] = [
  {
    id: 'grp-1',
    assignmentId: 'asg-1',
    assignmentTitle: 'AWS VPC Infrastructure Design',
    name: 'Cloud Architects Alpha',
    maxSize: 3,
    isLocked: true,
    submissionStatus: 'Approved',
    submissionRepo: 'https://github.com/uni-cloud/vpc-alpha',
    submissionDoc: 'https://docs.uni.edu/vpc-spec.pdf',
    submittedAt: '2026-09-02',
    members: [
      { studentId: 'CS-8891', name: 'Alex Rivera', email: 'alex.rivera@student.edu', joinedAt: '2026-08-22' },
      { studentId: 'CS-8892', name: 'Liam Chen', email: 'liam.chen@student.edu', joinedAt: '2026-08-22' },
      { studentId: 'CS-8893', name: 'Sophia Patel', email: 'sophia.patel@student.edu', joinedAt: '2026-08-23' }
    ]
  },
  {
    id: 'grp-2',
    assignmentId: 'asg-3',
    assignmentTitle: 'PostgreSQL Schema Migration',
    name: 'Data Guardians',
    maxSize: 4,
    isLocked: false,
    submissionStatus: 'Not Submitted',
    members: [
      { studentId: 'CS-8891', name: 'Alex Rivera', email: 'alex.rivera@student.edu', joinedAt: '2026-08-29' },
      { studentId: 'CS-8895', name: 'Elena Rostova', email: 'elena.rostova@student.edu', joinedAt: '2026-08-30' }
    ]
  },
  {
    id: 'grp-3',
    assignmentId: 'asg-5',
    assignmentTitle: 'Nginx Load Balancer Config',
    name: 'Proxy Masters',
    maxSize: 5,
    isLocked: false,
    submissionStatus: 'Pending Review',
    submissionRepo: 'https://github.com/proxy-masters/nginx-lb',
    submissionDoc: 'https://docs.uni.edu/nginx-report.pdf',
    submittedAt: '2026-09-04',
    members: [
      { studentId: 'CS-8901', name: 'Marcus Vance', email: 'marcus.vance@student.edu', joinedAt: '2026-09-01' },
      { studentId: 'CS-8902', name: 'Aaliyah Jones', email: 'aaliyah.jones@student.edu', joinedAt: '2026-09-01' },
      { studentId: 'CS-8903', name: 'David Kim', email: 'david.kim@student.edu', joinedAt: '2026-09-02' }
    ]
  }
];

export const INITIAL_SUBMISSIONS: Submission[] = [
  {
    id: 'sub-1',
    assignmentTitle: 'Nginx Load Balancer Config',
    groupName: 'Proxy Masters',
    submitterName: 'Marcus Vance',
    repoUrl: 'https://github.com/proxy-masters/nginx-lb',
    docUrl: 'https://docs.uni.edu/nginx-report.pdf',
    submittedDate: '2026-09-04',
    status: 'PENDING',
    reviewNotes: 'Pending review by instructor.'
  },
  {
    id: 'sub-2',
    assignmentTitle: 'AWS VPC Infrastructure Design',
    groupName: 'Cloud Architects Alpha',
    submitterName: 'Alex Rivera',
    repoUrl: 'https://github.com/uni-cloud/vpc-alpha',
    docUrl: 'https://docs.uni.edu/vpc-spec.pdf',
    submittedDate: '2026-09-02',
    status: 'APPROVED',
    reviewNotes: 'Excellent multi-AZ fault tolerance and documentation.'
  },
  {
    id: 'sub-3',
    assignmentTitle: 'Redis Cache Optimization',
    groupName: 'Dev Sprint #4',
    submitterName: 'Chloe Bennett',
    repoUrl: 'https://github.com/cbennett/redis-opt',
    docUrl: 'https://docs.uni.edu/redis-benchmark.pdf',
    submittedDate: '2026-08-31',
    status: 'REJECTED',
    reviewNotes: 'Cache invalidation logic missing for concurrent write scenarios. Please revise.'
  }
];
