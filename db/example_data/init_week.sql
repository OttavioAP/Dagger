INSERT INTO week (id, start_date, end_date, user_id, summary, feedback, collaborators, missed_deadlines, completed_tasks, points_completed, embedding)
VALUES (
    gen_random_uuid(),
    '2024-06-03 00:00:00',
    '2024-06-09 23:59:59',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'Summary for the week',
    'Feedback for the week',
    ARRAY['4fa85f64-5717-4562-b3fc-2c963f66afa7', '3fa85f64-5717-4562-b3fc-2c963f66afa6']::uuid[],
    ARRAY['11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222']::uuid[],
    ARRAY['33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444']::uuid[],
    42,
    '[0.1, 0.2, 0.3]'::vector(1536)
);
