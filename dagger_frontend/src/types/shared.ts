import type { components } from './api';

export type User = components['schemas']['user'];
export type Team = components['schemas']['team'];
export type Task = components['schemas']['task'];
export type Week = components['schemas']['week'];
export type Dag = components['schemas']['dag'];
export type UserTask = components['schemas']['user_tasks'];

// Enums
export type TaskPriority = components['schemas']['TaskPriority'];
export type TaskFocus = components['schemas']['TaskFocus'];
export type TaskAction = components['schemas']['task_action'];
export type DagAction = components['schemas']['DagAction'];
export type WeekRequestType = components['schemas']['WeekRequestType'];
export type UpdateUserOption = components['schemas']['UpdateUserOption'];
export type Option = components['schemas']['option'];
export type SearchType = components['schemas']['SearchType'];

// Request/Response types
export type UpdateUserRequest = components['schemas']['UpdateUserRequest'];
export type CreateTeamRequest = components['schemas']['CreateTeamRequest'];
export type TaskRequest = components['schemas']['TaskRequest'];
export type DagRequest = components['schemas']['DagRequest'];
export type UserTasksRequest = components['schemas']['UserTasksRequest'];
export type WeekResponse = components['schemas']['WeekResponse'];
export type DagResponse = components['schemas']['DagResponse'];
export type SearchResponse = components['schemas']['SearchResponse']; 