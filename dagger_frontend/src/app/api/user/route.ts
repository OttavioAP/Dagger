import { NextRequest, NextResponse } from 'next/server';
import { updateUserUserPost, getUserByUsernameUserGetUserByUsernameGet } from '@/client/sdk.gen';
import type { UpdateUserRequest, User } from '@/client/types.gen';

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as UpdateUserRequest;

    // Call FastAPI backend via generated client
    const response = await updateUserUserPost({
      body,
    });

    // Return the backend response to the frontend
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

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const username = searchParams.get('username');
    if (!username) {
      return NextResponse.json({ error: 'Username is required' }, { status: 400 });
    }
    const response = await getUserByUsernameUserGetUserByUsernameGet({
      query: { username },
    });
    if (!response) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
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
