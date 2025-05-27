import { NextRequest, NextResponse } from 'next/server';
import { getWeeksWeekGet } from '@/client/sdk.gen';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get('user_id');
    const team_id = searchParams.get('team_id');
    const number_of_weeks = parseInt(searchParams.get('number_of_weeks') || '5', 10);
    const start_date = searchParams.get('start_date');
    const end_date = searchParams.get('end_date');

    const response = await getWeeksWeekGet({
      query: {
        request_type: 'get_weeks',
        number_of_weeks,
        user_id: user_id || undefined,
        team_id: team_id || undefined,
        start_date: start_date || undefined,
        end_date: end_date || undefined
      }
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
