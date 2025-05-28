import { NextRequest, NextResponse } from 'next/server';
import { dagActionDagPost, getAllDagsDagGet } from '@/client/sdk.gen';
import type { DagRequest } from '@/client/types.gen';

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as DagRequest;
    const response = await dagActionDagPost({ body });
    return NextResponse.json(response.data, { status: 200 });
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
    const response = await getAllDagsDagGet();
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
