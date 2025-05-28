import { NextRequest, NextResponse } from 'next/server';
import { agenticSearchAgenticSearchGet } from '@/client/sdk.gen';
import type { SearchType, SearchResponse } from '@/types/shared';

const VALID_SEARCH_TYPES: SearchType[] = ['regular', 'semantic', 'compare'];

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const search_type = searchParams.get('search_type');
    const query = searchParams.get('query');
    const week_id = searchParams.get('week_id');
    const number_of_weeks = parseInt(searchParams.get('number_of_weeks') || '5', 10);
    const start_date = searchParams.get('start_date');
    const end_date = searchParams.get('end_date');
    const user_id = searchParams.get('user_id');
    const team_id = searchParams.get('team_id');
    const collaborators = searchParams.getAll('collaborators');
    const missed_deadlines_range = searchParams.get('missed_deadlines_range')?.split(',').map(Number);
    const completed_task_range = searchParams.get('completed_task_range')?.split(',').map(Number);
    const points_range = searchParams.get('points_range')?.split(',').map(Number);

    // Validate required parameters based on search type
    if (!search_type || !VALID_SEARCH_TYPES.includes(search_type as SearchType)) {
      return NextResponse.json({ error: 'search_type is required and must be one of: regular, semantic, compare' }, { status: 400 });
    }

    // At this point, search_type is guaranteed to be a valid SearchType
    const validSearchType = search_type as SearchType;

    if (validSearchType === 'regular' || validSearchType === 'semantic') {
      if (!query) {
        return NextResponse.json({ error: 'query is required for regular and semantic search' }, { status: 400 });
      }
    }

    if (validSearchType === 'compare') {
      if (!week_id) {
        return NextResponse.json({ error: 'week_id is required for comparison search' }, { status: 400 });
      }
    }

    // Construct the query parameters
    function toTupleOrNull(arr?: number[]): [number, number] | null {
      return arr && arr.length === 2 ? [arr[0], arr[1]] : null;
    }
    const queryParams = {
      search_type: validSearchType,
      query: query || null,
      week_id: week_id || null,
      number_of_weeks,
      start_date: start_date || null,
      end_date: end_date || null,
      user_id: user_id || null,
      team_id: team_id || null,
      collaborators: collaborators.length > 0 ? collaborators : null,
      missed_deadlines_range: toTupleOrNull(missed_deadlines_range),
      completed_task_range: toTupleOrNull(completed_task_range),
      points_range: toTupleOrNull(points_range)
    };

    const response = await agenticSearchAgenticSearchGet({
      query: queryParams
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
