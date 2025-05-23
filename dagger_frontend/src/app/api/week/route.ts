import { NextRequest, NextResponse } from 'next/server';
import { getWeeksWeekGet } from '@/client/sdk.gen';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get('user_id');
    const team_id = searchParams.get('team_id');
    const query: Record<string, string | null> = {};
    if (user_id) query.user_id = user_id;
    if (team_id) query.team_id = team_id;
    const response = await getWeeksWeekGet({ query: Object.keys(query).length ? query : undefined });
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
