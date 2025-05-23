import { NextRequest, NextResponse } from 'next/server';
import { agenticSearchAgenticSearchGet } from '@/client/sdk.gen';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const query = searchParams.get('query');
    const username = searchParams.get('username');
    const team_name = searchParams.get('team_name');
    if (!query || !username || !team_name) {
      return NextResponse.json({ error: 'query, username, and team_name are required' }, { status: 400 });
    }
    const response = await agenticSearchAgenticSearchGet({
      query: { query, username, team_name },
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
