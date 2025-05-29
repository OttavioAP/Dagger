"use client";

import React, { useState, useEffect } from 'react';
import { useData } from '../contexts/data_context';
import WeekComponent from '../components/week';
import type { Week } from '@/client/types.gen';

export default function DataView() {
  const { weeks, loading, error } = useData();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState<Date[]>([]);

  // Generate calendar days for the current month
  useEffect(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    // Get first day of month and last day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Get the day of week for first day (0 = Sunday, 6 = Saturday)
    const firstDayOfWeek = firstDay.getDay();
    
    // Calculate days to show from previous month
    const daysFromPrevMonth = firstDayOfWeek;
    
    // Calculate total days to show (including padding)
    const totalDays = Math.ceil((lastDay.getDate() + daysFromPrevMonth) / 7) * 7;
    
    const days: Date[] = [];
    
    // Add days from previous month
    for (let i = daysFromPrevMonth - 1; i >= 0; i--) {
      days.push(new Date(year, month, -i));
    }
    
    // Add days from current month
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push(new Date(year, month, i));
    }
    
    // Add days from next month
    const remainingDays = totalDays - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      days.push(new Date(year, month + 1, i));
    }
    
    setCalendarDays(days);
  }, [currentMonth]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + (direction === 'next' ? 1 : -1), 1));
  };

  const getWeekForDate = (date: Date): Week | undefined => {
    return weeks.find(week => {
      const weekStart = new Date(week.start_date);
      const weekEnd = new Date(week.end_date);
      return date >= weekStart && date <= weekEnd;
    });
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => navigateMonth('prev')}
          className="px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 rounded"
        >
          Previous
        </button>
        <h1 className="text-2xl font-bold">
          {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h1>
        <button
          onClick={() => navigateMonth('next')}
          className="px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 rounded"
        >
          Next
        </button>
      </div>

      {loading ? (
        <div className="text-center py-4">Loading...</div>
      ) : error ? (
        <div className="text-red-500 text-center py-4">{error}</div>
      ) : (
        <div className="grid grid-cols-7 gap-1">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-center font-medium py-2">
              {day}
            </div>
          ))}
          
          {calendarDays.map((date, index) => {
            const isCurrentMonth = date.getMonth() === currentMonth.getMonth();
            const isSaturday = date.getDay() === 6;
            const week = isSaturday ? getWeekForDate(date) : undefined;
            
            return (
              <div
                key={index}
                className={`
                  min-h-[100px] p-1 border border-gray-200
                  ${!isCurrentMonth ? 'bg-gray-50' : ''}
                  ${isSaturday ? 'bg-blue-50' : ''}
                `}
              >
                <div className="text-sm text-gray-500">
                  {date.getDate()}
                </div>
                {week && (
                  <WeekComponent
                    week={week}
                    onClick={() => console.log('Week clicked:', week)}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
