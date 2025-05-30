'use client';
import React from 'react';
import type { Week } from '@/client/types.gen';

interface WeekProps {
  week: Week;
  onClick?: () => void;
}

export default function WeekComponent({ week, onClick }: WeekProps) {
  const startDate = new Date(week.start_date);
  const endDate = new Date(week.end_date);
  
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div 
      onClick={onClick}
      className="p-2 bg-blue-500/10 hover:bg-blue-500/20 rounded cursor-pointer transition-colors"
    >
      <div className="text-sm font-medium">
        {formatDate(startDate)} - {formatDate(endDate)}
      </div>
    </div>
  );
}
