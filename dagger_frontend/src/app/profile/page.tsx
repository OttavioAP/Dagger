'use client';

import { useAuth } from '@/app/contexts/auth_context';

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Please log in to view your profile</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-4">Profile</h1>
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-700">
            Username: <span className="font-semibold">{user.username}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
