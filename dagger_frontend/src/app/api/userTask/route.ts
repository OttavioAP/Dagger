import { NextRequest, NextResponse } from 'next/server';
import { getAllUserTasksUserTasksGet, modifyUserTaskUserTasksPost } from '@/client/sdk.gen';
import type { UserTasksRequest } from '@/client/types.gen';

export async function GET() {
  try {
    const response = await getAllUserTasksUserTasksGet();
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
    const body = (await req.json()) as UserTasksRequest;
    const response = await modifyUserTaskUserTasksPost({ body });
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
