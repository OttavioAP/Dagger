import { NextRequest, NextResponse } from 'next/server';
import { getAllTasksByTeamTasksTeamIdGet, taskActionTasksPost } from '@/client/sdk.gen';
import type { TaskRequest } from '@/client/types.gen';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const team_id = searchParams.get('team_id');
    if (!team_id) {
      return NextResponse.json({ error: 'team_id is required' }, { status: 400 });
    }
    const response = await getAllTasksByTeamTasksTeamIdGet({
      path: { team_id },
    });
    return NextResponse.json(response, { status: 200 });
  } catch (error: unknown) {
    const message =
      typeof error === 'object' && error !== null && 'message' in error
        ? String((error as { message?: unknown }).message)
        : 'Internal Server Error';
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as TaskRequest;
    const response = await taskActionTasksPost({ body });
    return NextResponse.json(response, { status: 201 });
  } catch (error: unknown) {
    const message =
      typeof error === 'object' && error !== null && 'message' in error
        ? String((error as { message?: unknown }).message)
        : 'Internal Server Error';
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
