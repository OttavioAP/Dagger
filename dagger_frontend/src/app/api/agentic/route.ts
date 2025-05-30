import { NextRequest, NextResponse } from 'next/server';
import { chatAgenticChatGet } from '@/client/sdk.gen';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const query = searchParams.get('query');
    const user_id = searchParams.get('user_id');

    if (!query || !user_id) {
      return NextResponse.json({ error: 'query and user_id are required' }, { status: 400 });
    }

    const chatResponse = await chatAgenticChatGet({
      query: { query, user_id },
    });

    return NextResponse.json(chatResponse, { status: 200 });
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
